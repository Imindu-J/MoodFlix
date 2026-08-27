import time
from typing import Any 

import httpx

from app.schemas.tmdb import TmdbDiscoverResponse, TmdbMovieDetails


RETRYABLE_STATUS_CODE = { 429, 500, 502, 503, 504}

class TmdbClient:
    def __init__(
            self,
            access_token: str,
            base_url: str,
            timeout_seconds: float,
            max_attempts: int = 4,
            ) -> None:
        self.max_attempts = max_attempts
        self.client = httpx.Client(
            base_url=f"{base_url.rstrip('/')}/",
            timeout=timeout_seconds,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            },
        )


    def __enter__(self) -> TmdbClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
    
    def close(self) -> None:
        self.client.close()

    def discover_movies(
            self,
            page: int,
            minimum_vote_count: int = 200,
    ) -> TmdbDiscoverResponse:
        data = self._get(
            "discover/movie",
            params={
                "page": page,
                "sort_by": "popularity.desc",
                "include_adult": "true",
                "vote_count.gte": minimum_vote_count,
                "language": "en-US",
            },
        )
        return TmdbDiscoverResponse.model_validate(data)
    

    def get_movie_details(self, movie_id: int) -> TmdbMovieDetails:
        data = self._get(
            f"movie/{movie_id}",
            params={
                "append_to_response": "keywords, release_dates",
                "language": "en-US",
            },
        )
        return TmdbMovieDetails.model_validate(data)


    def _get(
            self,
            path: str,
            params: dict[str: Any] | None = None,
    ) -> dict[str, Any]:
        for attempt in range(1, self.max_attempts +1):
            try:
                response = self.client.get(path, params=params)

                if response.status_code in RETRYABLE_STATUS_CODE:
                    if attempt == self.max_attempts:
                        response.raise_for_status()

                    time.sleep(self._retry_delay(response, attempt))
                    continue

                response.raise_for_status()
                return response.json()

            except httpx.TransportError:
                if attempt==self.max_attempts:
                    raise

                time.sleep(self._retry_delay(None, attempt))

        raise RuntimeError("TMDB request failed unexpectedly")


    @staticmethod
    def _retry_delay(
        response: httpx.Response | None,
        attempt: int,
    ) -> float:
        if response is not None:
            retry_after = response.headers.get("Retry-After")

            if retry_after:
                try: 
                    return max(0, float(retry_after))
                except ValueError:
                    pass

        return min(2** (attempt -1), 30)
        
    
