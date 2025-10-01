# backend/routers/debug_openai.py
# Debug router to test OpenAI client initialization

import os
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/test-openai")
async def test_openai_client():
    """Test OpenAI client initialization to debug the proxies error"""
    
    debug_info = {
        "openai_api_key_set": bool(os.getenv("OPENAI_API_KEY")),
        "openai_api_base": os.getenv("OPENAI_API_BASE", "not_set"),
        "test_results": []
    }
    
    # Test 1: Try importing OpenAI
    try:
        from openai import OpenAI
        debug_info["test_results"].append({
            "test": "import_openai",
            "status": "success",
            "message": "OpenAI import successful"
        })
    except Exception as e:
        debug_info["test_results"].append({
            "test": "import_openai", 
            "status": "error",
            "message": f"OpenAI import failed: {str(e)}"
        })
        return debug_info
    
    # Test 2: Try creating OpenAI client (correct way)
    try:
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "test-key"),
            base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        )
        debug_info["test_results"].append({
            "test": "create_client_correct",
            "status": "success", 
            "message": "OpenAI client created successfully (correct method)"
        })
    except Exception as e:
        debug_info["test_results"].append({
            "test": "create_client_correct",
            "status": "error",
            "message": f"OpenAI client creation failed: {str(e)}"
        })
    
    # Test 3: Try creating OpenAI client (old way with proxies - should fail)
    try:
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "test-key"),
            proxies=None  # This should cause the error
        )
        debug_info["test_results"].append({
            "test": "create_client_with_proxies",
            "status": "unexpected_success",
            "message": "OpenAI client with proxies worked (this shouldn't happen)"
        })
    except Exception as e:
        debug_info["test_results"].append({
            "test": "create_client_with_proxies",
            "status": "expected_error",
            "message": f"Expected error with proxies: {str(e)}"
        })
    
    # Test 4: Check OpenAI version
    try:
        import openai
        debug_info["openai_version"] = openai.__version__
    except:
        debug_info["openai_version"] = "unknown"
    
    return debug_info

@router.get("/health")
async def debug_health():
    """Simple health check for debug router"""
    return {"status": "debug_router_working", "message": "Debug router is loaded and functional"}
