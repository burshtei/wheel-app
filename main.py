"""
FastAPI web service for Wheel Strategy Stock Analyzer
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
from src.analyzer import WheelAnalyzer
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Wheel Strategy Stock Analyzer API",
    description="API for analyzing stocks suitable for the options wheel strategy",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzer
analyzer = WheelAnalyzer()


# Request/Response models
class ScreenRequest(BaseModel):
    tickers: Optional[List[str]] = Field(None, description="List of ticker symbols to screen")
    min_market_cap: Optional[float] = Field(None, description="Minimum market cap")
    min_iv_rank: Optional[float] = Field(None, description="Minimum IV rank")
    min_options_volume: Optional[int] = Field(None, description="Minimum options volume")


class AnalyzeRequest(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    target_dte: Optional[int] = Field(None, description="Target days to expiration")


class CompareRequest(BaseModel):
    tickers: List[str] = Field(..., description="List of ticker symbols to compare")
    strategy: str = Field("put", description="Strategy type: 'put' or 'call'")
    target_dte: Optional[int] = Field(None, description="Target days to expiration")


class BestCandidatesRequest(BaseModel):
    min_annual_return: float = Field(20.0, description="Minimum annualized return (%)")
    max_results: int = Field(10, description="Maximum number of results")


# Helper function to convert DataFrame to dict
def df_to_dict(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Convert DataFrame to list of dictionaries"""
    if df.empty:
        return []
    return df.to_dict('records')


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Wheel Strategy Stock Analyzer API",
        "version": "1.0.0",
        "endpoints": [
            "/health",
            "/screen",
            "/analyze/{ticker}",
            "/compare",
            "/best-candidates"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "wheel-analyzer"}


@app.post("/screen")
async def screen_stocks(request: ScreenRequest):
    """
    Screen stocks for wheel strategy suitability.

    Returns a list of stocks that pass the screening criteria.
    """
    try:
        logger.info(f"Screening stocks with criteria: {request.dict()}")

        results = analyzer.screen_stocks(
            tickers=request.tickers,
            min_market_cap=request.min_market_cap,
            min_iv_rank=request.min_iv_rank,
            min_options_volume=request.min_options_volume
        )

        return {
            "success": True,
            "count": len(results),
            "results": df_to_dict(results)
        }
    except Exception as e:
        logger.error(f"Error screening stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analyze/{ticker}")
async def analyze_ticker(
    ticker: str,
    target_dte: Optional[int] = Query(None, description="Target days to expiration")
):
    """
    Analyze a specific ticker for wheel strategy opportunities.

    Returns both put and call opportunities.
    """
    try:
        logger.info(f"Analyzing ticker: {ticker}")

        analysis = analyzer.analyze_ticker(ticker, target_dte)

        # Get put and call opportunities
        put_opportunities = analysis.get_put_opportunities()
        call_opportunities = analysis.get_call_opportunities()

        return {
            "success": True,
            "ticker": ticker,
            "current_price": analysis.current_price,
            "expiration_date": analysis.expiration_date,
            "put_opportunities": df_to_dict(put_opportunities),
            "call_opportunities": df_to_dict(call_opportunities)
        }
    except Exception as e:
        logger.error(f"Error analyzing ticker {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compare")
async def compare_opportunities(request: CompareRequest):
    """
    Compare wheel strategy opportunities across multiple tickers.
    """
    try:
        logger.info(f"Comparing opportunities for: {request.tickers}")

        results = analyzer.compare_opportunities(
            tickers=request.tickers,
            strategy=request.strategy,
            target_dte=request.target_dte
        )

        return {
            "success": True,
            "strategy": request.strategy,
            "count": len(results),
            "results": df_to_dict(results)
        }
    except Exception as e:
        logger.error(f"Error comparing opportunities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/best-candidates")
async def find_best_candidates(request: BestCandidatesRequest):
    """
    Find the best wheel strategy candidates based on screening and analysis.
    """
    try:
        logger.info(f"Finding best candidates with min return: {request.min_annual_return}%")

        results = analyzer.find_best_wheel_candidates(
            min_annual_return=request.min_annual_return,
            max_results=request.max_results
        )

        return {
            "success": True,
            "count": len(results),
            "results": df_to_dict(results)
        }
    except Exception as e:
        logger.error(f"Error finding best candidates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ticker/{ticker}/puts")
async def get_put_opportunities(
    ticker: str,
    target_dte: Optional[int] = Query(None, description="Target days to expiration"),
    min_premium: Optional[float] = Query(None, description="Minimum premium per share")
):
    """
    Get cash-secured put opportunities for a specific ticker.
    """
    try:
        logger.info(f"Getting put opportunities for: {ticker}")

        analysis = analyzer.analyze_ticker(ticker, target_dte)
        opportunities = analysis.get_put_opportunities(min_premium=min_premium)

        return {
            "success": True,
            "ticker": ticker,
            "current_price": analysis.current_price,
            "opportunities": df_to_dict(opportunities)
        }
    except Exception as e:
        logger.error(f"Error getting put opportunities for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ticker/{ticker}/calls")
async def get_call_opportunities(
    ticker: str,
    target_dte: Optional[int] = Query(None, description="Target days to expiration"),
    min_premium: Optional[float] = Query(None, description="Minimum premium per share"),
    cost_basis: Optional[float] = Query(None, description="Your cost basis")
):
    """
    Get covered call opportunities for a specific ticker.
    """
    try:
        logger.info(f"Getting call opportunities for: {ticker}")

        analysis = analyzer.analyze_ticker(ticker, target_dte)
        opportunities = analysis.get_call_opportunities(
            min_premium=min_premium,
            cost_basis=cost_basis
        )

        return {
            "success": True,
            "ticker": ticker,
            "current_price": analysis.current_price,
            "opportunities": df_to_dict(opportunities)
        }
    except Exception as e:
        logger.error(f"Error getting call opportunities for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
