#!/bin/bash
gcloud builds submit --tag gcr.io/$PROJECT_ID/rag-backend backend/
gcloud run deploy rag-backend --image gcr.io/$PROJECT_ID/rag-backend --platform managed
# Similarly for frontend
