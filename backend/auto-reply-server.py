"""
OneCloud Support Chatbot API - Auto-Reply System
Uses user's dataset for automatic bot responses based on conversation flow
"""

import os
import json
import sqlite3
import uuid
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    APP_NAME = "OneCloud Support Chatbot API"
    VERSION = "1.0.0"
    HOST = "0.0.0.0"
    PORT = int(os.getenv("PORT", 7860))
    DATASET_PATH = "../dataset"
    ENGLISH_DATASET = "dataset-for-chat-eng.json"
    MYANMAR_DATASET = "dataset-for-chat-mm.json"
    HANDOFF_EMAIL = "support@onecloud.com"
    HANDOFF_PHONE = "+95-9-123456789"

# Pydantic Models
class ChatMessage(BaseModel):
    message: str
    language: str = "en"
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    language: str
    category: Optional[str] = None
    intent: Optional[str] = None
    handoff_required: bool = False
    suggestions: List[str] = []
    timestamp: str

# Auto-Reply Dataset Manager
class AutoReplyDatasetManager:
    def __init__(self):
        self.english_data = []
        self.myanmar_data = []
        self.question_answer_pairs = {}  # For exact matching
        self.intent_responses = {}  # For intent-based responses
        self._load_datasets()
        self._build_auto_reply_system()
    
    def _load_datasets(self):
        """Load user's dataset files"""
        try:
            # Load English dataset
            eng_path = Path(Config.DATASET_PATH) / Config.ENGLISH_DATASET
            logger.info(f"🔍 Looking for English dataset at: {eng_path}")
            if eng_path.exists():
                with open(eng_path, 'r', encoding='utf-8') as f:
                    self.english_data = json.load(f)
                logger.info(f"✅ Loaded {len(self.english_data)} English entries")
                # Log first few entries for debugging
                for i, item in enumerate(self.english_data[:3]):
                    logger.info(f"📝 English entry {i+1}: {item.get('role')} - {item.get('message', '')[:50]}... - locale: {item.get('locale')}")
            else:
                logger.error(f"❌ English dataset not found at: {eng_path}")
            
            # Load Myanmar dataset
            mm_path = Path(Config.DATASET_PATH) / Config.MYANMAR_DATASET
            logger.info(f"🔍 Looking for Myanmar dataset at: {mm_path}")
            if mm_path.exists():
                with open(mm_path, 'r', encoding='utf-8') as f:
                    self.myanmar_data = json.load(f)
                logger.info(f"✅ Loaded {len(self.myanmar_data)} Myanmar entries")
            else:
                logger.error(f"❌ Myanmar dataset not found at: {mm_path}")
                
        except Exception as e:
            logger.error(f"❌ Failed to load datasets: {e}")
    
    def _build_auto_reply_system(self):
        """Build auto-reply system from user's dataset"""
        logger.info(f"🔗 Building auto-reply system from datasets")
        
        # Process English dataset separately
        self._process_language_dataset(self.english_data, 'en')
        
        # Process Myanmar dataset separately  
        self._process_language_dataset(self.myanmar_data, 'mm')
        
        logger.info(f"🤖 Built auto-reply system:")
        logger.info(f"   - English Q&A pairs: {len(self.question_answer_pairs.get('en', {}))}")
        logger.info(f"   - Myanmar Q&A pairs: {len(self.question_answer_pairs.get('mm', {}))}")
        logger.info(f"   - English intents: {len(self.intent_responses.get('en', {}))}")
        logger.info(f"   - Myanmar intents: {len(self.intent_responses.get('mm', {}))}")
    
    def _process_language_dataset(self, dataset_data, language):
        """Process a single language dataset"""
        # Group by conversation_id to build Q&A pairs
        conversations = {}
        for item in dataset_data:
            conv_id = item.get('conversation_id')
            if conv_id not in conversations:
                conversations[conv_id] = []
            conversations[conv_id].append(item)
        
        logger.info(f"🔗 Processing {len(conversations)} {language} conversations from {len(dataset_data)} entries")
        
        # Build Q&A pairs and intent mappings
        for conv_id, messages in conversations.items():
            customer_msg = None
            bot_msg = None
            
            for msg in messages:
                if msg.get('role') == 'customer':
                    customer_msg = msg
                elif msg.get('role') == 'bot':
                    bot_msg = msg
            
            if customer_msg and bot_msg:
                # Store exact question-answer pairs
                question = customer_msg['message'].strip().lower()
                locale = customer_msg.get('locale', '').lower()
                
                logger.info(f"🔍 Processing {language}: conv_id={customer_msg.get('conversation_id')}, locale={locale}, question='{question}'")
                
                if language not in self.question_answer_pairs:
                    self.question_answer_pairs[language] = {}
                
                self.question_answer_pairs[language][question] = {
                    'answer': bot_msg['message'],
                    'category': customer_msg.get('category'),
                    'intent': customer_msg.get('intent'),
                    'handoff_required': customer_msg.get('handoff_required') == 'yes',
                    'locale': customer_msg.get('locale')
                }
                
                # Store intent-based responses
                intent = customer_msg.get('intent')
                if intent and language not in self.intent_responses:
                    self.intent_responses[language] = {}
                
                if intent:
                    if intent not in self.intent_responses[language]:
                        self.intent_responses[language][intent] = []
                    
                    self.intent_responses[language][intent].append({
                        'answer': bot_msg['message'],
                        'category': customer_msg.get('category'),
                        'handoff_required': customer_msg.get('handoff_required') == 'yes',
                        'question': customer_msg['message']
                    })
            else:
                logger.warning(f"⚠️ Incomplete {language} conversation {conv_id}: customer={bool(customer_msg)}, bot={bool(bot_msg)}")
    
    def get_auto_reply(self, user_message: str, language: str = 'en') -> Dict[str, Any]:
        """Get auto-reply based on user's dataset"""
        
        # Normalize user message
        normalized_message = user_message.strip().lower()
        
        # 1. Try exact match first
        if language in self.question_answer_pairs:
            if normalized_message in self.question_answer_pairs[language]:
                response_data = self.question_answer_pairs[language][normalized_message]
                logger.info(f"🎯 Exact match found for: '{user_message}'")
                return {
                    'answer': response_data['answer'],
                    'category': response_data['category'],
                    'intent': response_data['intent'],
                    'handoff_required': response_data['handoff_required'],
                    'match_type': 'exact'
                }
        
        # 2. Try partial match (contains)
        if language in self.question_answer_pairs:
            for question, response_data in self.question_answer_pairs[language].items():
                if normalized_message in question or question in normalized_message:
                    logger.info(f"🔍 Partial match found: '{user_message}' -> '{question}'")
                    return {
                        'answer': response_data['answer'],
                        'category': response_data['category'],
                        'intent': response_data['intent'],
                        'handoff_required': response_data['handoff_required'],
                        'match_type': 'partial'
                    }
        
        # 3. Try keyword-based matching
        if language in self.question_answer_pairs:
            best_match = None
            best_score = 0
            
            for question, response_data in self.question_answer_pairs[language].items():
                # Simple keyword matching
                user_words = set(normalized_message.split())
                question_words = set(question.split())
                
                if user_words and question_words:
                    intersection = user_words.intersection(question_words)
                    score = len(intersection) / len(user_words)
                    
                    if score > best_score and score > 0.3:  # 30% minimum match
                        best_score = score
                        best_match = {
                            'answer': response_data['answer'],
                            'category': response_data['category'],
                            'intent': response_data['intent'],
                            'handoff_required': response_data['handoff_required'],
                            'match_type': 'keyword',
                            'confidence': score
                        }
            
            if best_match:
                logger.info(f"🔑 Keyword match found: '{user_message}' (confidence: {best_score:.2f})")
                return best_match
        
        # 4. No response if not in dataset
        logger.info(f"❌ No match found for: '{user_message}', no response")
        return {
            'answer': '',
            'category': None,
            'intent': None,
            'handoff_required': False,
            'match_type': 'no_match'
        }
    
    def get_faq_by_category(self, language: str = 'en', category: str = None):
        """Get FAQ from auto-reply system"""
        faqs = []
        
        if language in self.question_answer_pairs:
            for question, response_data in self.question_answer_pairs[language].items():
                if category and response_data.get('category') != category:
                    continue
                
                faqs.append({
                    'question': question.capitalize(),
                    'answer': response_data['answer'],
                    'category': response_data.get('category'),
                    'intent': response_data.get('intent'),
                    'handoff_required': response_data.get('handoff_required', False)
                })
        
        return faqs
    
    def search_faq(self, query: str, language: str = 'en', limit: int = 5):
        """Search FAQ from auto-reply system"""
        query_lower = query.lower()
        
        all_faqs = self.get_faq_by_category(language)
        
        # Score matches
        scored_faqs = []
        for faq in all_faqs:
            question_lower = faq['question'].lower()
            words_in_query = set(query_lower.split())
            words_in_question = set(question_lower.split())
            
            if words_in_query:
                intersection = words_in_query.intersection(words_in_question)
                score = len(intersection) / len(words_in_query)
                
                if score > 0.1:  # 10% minimum match
                    faq_copy = faq.copy()
                    faq_copy['relevance'] = score
                    scored_faqs.append(faq_copy)
        
        # Sort by relevance and return top results
        scored_faqs.sort(key=lambda x: x['relevance'], reverse=True)
        return scored_faqs[:limit]

# Initialize services
auto_reply_manager = AutoReplyDatasetManager()

# Create FastAPI app
app = FastAPI(
    title="OneCloud Support Chatbot API - Auto-Reply System",
    description="Auto-reply chatbot using user's dataset conversation flow",
    version=Config.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper functions
def generate_suggestions(language: str, category: str) -> List[str]:
    """Generate contextual suggestions based on user's dataset"""
    if language == 'en':
        if category == 'sales':
            return ["How much is the pricing?", "What are the differences between packages?", "Is there a trial available?", "Contact sales team"]
        elif category == 'technical':
            return ["How do I integrate with my CRM?", "What APIs are available?", "Technical support needed", "Integration help"]
        elif category == 'billing':
            return ["How do I update my payment method?", "View my invoice", "Billing question", "Payment issue"]
        elif category == 'support':
            return ["I need help with my account", "Technical issue", "Contact support", "System status"]
        else:
            return ["Pricing Information", "Technical Support", "Account Setup", "Billing Questions"]
    else:  # Myanmar
        if category == 'sales':
            return ["Pricing ဘယ်လောက်လဲ?", "Package တွေ ဘာကွာလဲ?", "Trial ရနိုင်လား?", "ရောင်းအားအဖွဲ့နှင့်ဆက်သွယ်ရန်"]
        elif category == 'technical':
            return ["CRM နှင့်ဘယ်လိုချိတ်ဆက်မလဲ?", "API ဘယ်လိုမျိုးရနိုင်လဲ?", "နည်းပညာအကူအညီလိုတယ်", "ချိတ်ဆက်မှုကူညီပေးပါ"]
        elif category == 'billing':
            return ["ငွေပေးချေမှုနည်းလမ်းဘယ်လိုပြောင်းလဲ?", "ငွေစာရင်းကြည့်ရန်", "ငွေပေးချေမှုမေးခွန်း", "ငွေပေးချေပြဿနာ"]
        elif category == 'support':
            return ["အကောင့်ကူညီပေးရန်", "နည်းပညာပြဿနာ", "အထောက်အပံ့နှင့်ဆက်သွယ်ရန်", "စနစ်အခြေအနေ"]
        else:
            return ["စျေးနှုန်းသတင်း", "နည်းပညာအထောက်အပံ့", "အကောင့်ဖွဲ့စည်းခြင်း", "ငွေပေးချေမှုမေးခွန်းများ"]

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "OneCloud Support Chatbot API - Auto-Reply System",
        "version": Config.VERSION,
        "status": "running",
        "dataset_info": {
            "english_entries": len(auto_reply_manager.english_data),
            "myanmar_entries": len(auto_reply_manager.myanmar_data),
            "english_qa_pairs": len(auto_reply_manager.question_answer_pairs.get('en', {})),
            "myanmar_qa_pairs": len(auto_reply_manager.question_answer_pairs.get('mm', {}))
        },
        "auto_reply_features": [
            "Exact question matching",
            "Partial text matching", 
            "Keyword-based matching",
            "Bilingual support (EN/MM)",
            "Intent-based responses",
            "Handoff detection"
        ],
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "chat": "/api/v1/chat",
            "faq": "/api/v1/faq", 
            "health": "/api/v1/health",
            "docs": "/docs"
        }
    }

@app.post("/api/v1/chat/message")
async def send_message(message: ChatMessage):
    """Send message and get auto-reply from user's dataset"""
    try:
        # Generate conversation ID if not provided
        if not message.conversation_id:
            message.conversation_id = str(uuid.uuid4())
        
        # Get auto-reply from user's dataset
        response_data = auto_reply_manager.get_auto_reply(message.message, message.language)
        
        # Generate contextual suggestions
        suggestions = generate_suggestions(message.language, response_data.get('category', 'support'))
        
        # Log the interaction
        logger.info(f"💬 [{message.language.upper()}] User: '{message.message}'")
        logger.info(f"🤖 [{message.language.upper()}] Bot: '{response_data['answer'][:50]}...' (Match: {response_data['match_type']})")
        
        # Only respond if there's a match from dataset
        if response_data['answer']:
            return ChatResponse(
                message=response_data['answer'],
                conversation_id=message.conversation_id,
                language=message.language,
                category=response_data.get('category'),
                intent=response_data.get('intent'),
                handoff_required=response_data.get('handoff_required', False),
                suggestions=suggestions,
                timestamp=datetime.utcnow().isoformat()
            )
        else:
            # No response for unknown text - return appropriate message
            if message.language == 'en':
                no_response_msg = "I don't have information about that. Please ask about pricing, technical support, billing, or account setup."
            else:
                no_response_msg = "အဲဒီအကြောင်းအကြောင်းမရှိပါ။ စျေးနှုန်း၊ နည်းပညာအထောက်အပံ့၊ ငွေပေးချေမှု သို့မဟုတ် အကောင့်ဖွဲ့စည်းခြင်းအကြောင်းအရာများကိုမေးပါ။"
            
            return ChatResponse(
                message=no_response_msg,
                conversation_id=message.conversation_id,
                language=message.language,
                category=None,
                intent=None,
                handoff_required=False,
                suggestions=[],
                timestamp=datetime.utcnow().isoformat()
            )
        
    except Exception as e:
        logger.error(f"❌ Error processing message: {e}")
        raise HTTPException(status_code=500, detail="Failed to process message")

@app.get("/api/v1/faq/")
async def get_faq(language: str = "en", category: str = None, query: str = None, limit: int = 10):
    """Get FAQ from auto-reply system"""
    try:
        if query:
            faqs = auto_reply_manager.search_faq(query, language, limit)
        else:
            faqs = auto_reply_manager.get_faq_by_category(language, category)
        
        return {
            "items": faqs[:limit],
            "total": len(faqs),
            "language": language,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting FAQ: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve FAQ")

@app.get("/api/v1/health/")
async def health_check():
    """Comprehensive health check"""
    try:
        services = {
            "auto_reply_system": "healthy",
            "english_dataset": "healthy" if len(auto_reply_manager.english_data) > 0 else "degraded",
            "myanmar_dataset": "healthy" if len(auto_reply_manager.myanmar_data) > 0 else "degraded",
            "qa_pairs": "healthy" if len(auto_reply_manager.question_answer_pairs) > 0 else "degraded",
            "api": "healthy"
        }
        
        overall_status = "healthy" if all(status == "healthy" for status in services.values()) else "degraded"
        
        return {
            "status": overall_status,
            "version": Config.VERSION,
            "services": services,
            "dataset_stats": {
                "english_entries": len(auto_reply_manager.english_data),
                "myanmar_entries": len(auto_reply_manager.myanmar_data),
                "english_qa_pairs": len(auto_reply_manager.question_answer_pairs.get('en', {})),
                "myanmar_qa_pairs": len(auto_reply_manager.question_answer_pairs.get('mm', {}))
            },
            "auto_reply_stats": {
                "total_intents": len(auto_reply_manager.intent_responses.get('en', {})) + len(auto_reply_manager.intent_responses.get('mm', {})),
                "categories": list(set([item.get('category') for item in auto_reply_manager.english_data + auto_reply_manager.myanmar_data if item.get('category')]))
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Health check failed")

@app.get("/api/v1/health/simple")
async def simple_health():
    """Simple health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": Config.VERSION
    }

# Run the application
if __name__ == "__main__":
    print(f"🚀 Starting {Config.APP_NAME}")
    print(f"📊 Dataset: {len(auto_reply_manager.english_data)} English + {len(auto_reply_manager.myanmar_data)} Myanmar entries")
    print(f"🤖 Auto-Reply Pairs: {len(auto_reply_manager.question_answer_pairs.get('en', {}))} EN + {len(auto_reply_manager.question_answer_pairs.get('mm', {}))} MM")
    print(f"🌐 Server: http://{Config.HOST}:{Config.PORT}")
    print(f"📚 API Docs: http://{Config.HOST}:{Config.PORT}/docs")
    print(f"❤️  Health Check: http://{Config.HOST}:{Config.PORT}/api/v1/health/simple")
    print(f"💬 Test Chat: curl -X POST http://{Config.HOST}:{Config.PORT}/api/v1/chat/message -H 'Content-Type: application/json' -d '{{\"message\": \"How much is the pricing?\", \"language\": \"en\"}}'")
    print()
    
    uvicorn.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        log_level="info"
    )
