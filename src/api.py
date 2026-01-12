"""
FastAPI web service for Wheel Strategy Analyzer
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from src.analyzer import WheelAnalyzer
from src.screener import StockScreener
from src.utils import setup_logging

# Setup logging
setup_logging(log_level="INFO")
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Wheel Strategy Stock Analyzer API",
    description="REST API for analyzing stocks suitable for the options wheel strategy",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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


# Request/Response Models
class ScreenRequest(BaseModel):
    tickers: Optional[List[str]] = Field(None, description="List of tickers to screen")
    min_market_cap: Optional[float] = Field(None, description="Minimum market cap")
    min_iv_rank: Optional[float] = Field(None, description="Minimum IV rank")
    min_options_volume: Optional[int] = Field(None, description="Minimum options volume")


class TickerAnalysisRequest(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    target_dte: Optional[int] = Field(30, description="Target days to expiration")
    delta_min: Optional[float] = Field(0.20, description="Minimum delta")
    delta_max: Optional[float] = Field(0.35, description="Maximum delta")
    min_premium: Optional[float] = Field(None, description="Minimum premium")


class CompareRequest(BaseModel):
    tickers: List[str] = Field(..., description="List of tickers to compare")
    strategy: str = Field("put", description="Strategy type: 'put' or 'call'")
    target_dte: Optional[int] = Field(30, description="Target days to expiration")


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str


# API Endpoints
@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Wheel Strategy Stock Analyzer API",
        "version": "1.0.0",
        "description": "REST API for analyzing stocks suitable for the options wheel strategy",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "screen": "/api/v1/screen",
            "analyze": "/api/v1/analyze",
            "compare": "/api/v1/compare",
            "candidates": "/api/v1/candidates"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@app.post("/api/v1/screen", tags=["Screening"])
async def screen_stocks(request: ScreenRequest):
    """
    Screen stocks for wheel strategy suitability.

    Returns a list of stocks that meet the screening criteria.
    """
    try:
        logger.info(f"Screening stocks with criteria: {request.dict()}")

        results = analyzer.screen_stocks(
            tickers=request.tickers,
            min_market_cap=request.min_market_cap,
            min_iv_rank=request.min_iv_rank,
            min_options_volume=request.min_options_volume
        )

        if results.empty:
            return {
                "success": True,
                "count": 0,
                "results": [],
                "message": "No stocks passed screening criteria"
            }

        # Convert DataFrame to dict
        results_dict = results.to_dict('records')

        return {
            "success": True,
            "count": len(results_dict),
            "results": results_dict,
            "message": f"Found {len(results_dict)} candidates"
        }

    except Exception as e:
        logger.error(f"Error screening stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/analyze", tags=["Analysis"])
async def analyze_ticker(request: TickerAnalysisRequest):
    """
    Analyze a specific ticker for wheel strategy opportunities.

    Returns both put and call opportunities.
    """
    try:
        logger.info(f"Analyzing ticker: {request.ticker}")

        # Analyze ticker
        analysis = analyzer.analyze_ticker(
            request.ticker,
            target_dte=request.target_dte
        )

        # Get put opportunities
        put_opportunities = analysis.get_put_opportunities(
            delta_range=(request.delta_min, request.delta_max),
            min_premium=request.min_premium
        )

        # Get call opportunities
        call_opportunities = analysis.get_call_opportunities(
            delta_range=(request.delta_min, request.delta_max),
            min_premium=request.min_premium
        )

        return {
            "success": True,
            "ticker": request.ticker,
            "current_price": analysis.current_price,
            "expiration_date": analysis.expiration_date,
            "target_dte": request.target_dte,
            "put_opportunities": put_opportunities.to_dict('records') if not put_opportunities.empty else [],
            "call_opportunities": call_opportunities.to_dict('records') if not call_opportunities.empty else [],
            "put_count": len(put_opportunities),
            "call_count": len(call_opportunities)
        }

    except Exception as e:
        logger.error(f"Error analyzing {request.ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analyze/{ticker}", tags=["Analysis"])
async def analyze_ticker_get(
    ticker: str,
    target_dte: int = Query(30, description="Target days to expiration"),
    delta_min: float = Query(0.20, description="Minimum delta"),
    delta_max: float = Query(0.35, description="Maximum delta")
):
    """
    Analyze a specific ticker (GET method).
    """
    request = TickerAnalysisRequest(
        ticker=ticker,
        target_dte=target_dte,
        delta_min=delta_min,
        delta_max=delta_max
    )
    return await analyze_ticker(request)


@app.post("/api/v1/compare", tags=["Analysis"])
async def compare_opportunities(request: CompareRequest):
    """
    Compare wheel strategy opportunities across multiple tickers.
    """
    try:
        logger.info(f"Comparing {len(request.tickers)} tickers")

        results = analyzer.compare_opportunities(
            request.tickers,
            strategy=request.strategy,
            target_dte=request.target_dte
        )

        if results.empty:
            return {
                "success": True,
                "count": 0,
                "results": [],
                "message": "No opportunities found"
            }

        return {
            "success": True,
            "strategy": request.strategy,
            "target_dte": request.target_dte,
            "count": len(results),
            "results": results.to_dict('records')
        }

    except Exception as e:
        logger.error(f"Error comparing opportunities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/candidates", tags=["Screening"])
async def get_best_candidates(
    min_annual_return: float = Query(20.0, description="Minimum annualized return (%)"),
    max_results: int = Query(10, description="Maximum number of results")
):
    """
    Find the best wheel strategy candidates.
    """
    try:
        logger.info(f"Finding best candidates with min return {min_annual_return}%")

        results = analyzer.find_best_wheel_candidates(
            min_annual_return=min_annual_return,
            max_results=max_results
        )

        if results.empty:
            return {
                "success": True,
                "count": 0,
                "results": [],
                "message": f"No candidates meet minimum return of {min_annual_return}%"
            }

        return {
            "success": True,
            "count": len(results),
            "min_annual_return": min_annual_return,
            "results": results.to_dict('records')
        }

    except Exception as e:
        logger.error(f"Error finding candidates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/popular-tickers", tags=["Screening"])
async def get_popular_tickers():
    """
    Get list of popular tickers for wheel strategy.
    """
    try:
        screener = StockScreener()
        tickers = screener.get_popular_wheel_tickers()

        return {
            "success": True,
            "count": len(tickers),
            "tickers": tickers
        }

    except Exception as e:
        logger.error(f"Error getting popular tickers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/ticker/{ticker}/price", tags=["Market Data"])
async def get_ticker_price(ticker: str):
    """
    Get current price for a ticker.
    """
    try:
        from src.options_chain import OptionsChain

        chain = OptionsChain(ticker)
        price = chain.get_current_price()

        if price is None:
            raise HTTPException(status_code=404, detail=f"Price not found for {ticker}")

        return {
            "success": True,
            "ticker": ticker,
            "price": price,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting price for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "success": False,
        "error": "Not found",
        "detail": str(exc.detail) if hasattr(exc, 'detail') else "Resource not found"
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {
        "success": False,
        "error": "Internal server error",
        "detail": str(exc.detail) if hasattr(exc, 'detail') else "An unexpected error occurred"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
