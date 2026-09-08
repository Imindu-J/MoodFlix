from functools import lru_cache
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse, SimilarMoviesRequest
from app.services.embedding_service import EmbeddingService
from app.services.recommendation_service import MovieEmbeddingMissingError, MovieNotFound, RecommendationService


router = APIRouter(
    prefix="/recommendations",
    tags=["recommendation"]
)


