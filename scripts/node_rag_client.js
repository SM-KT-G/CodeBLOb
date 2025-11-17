// Simple Node.js wrapper for calling the FastAPI RAG backend
// Usage: 
//   node scripts/node_rag_client.js chat "ソウルでおすすめのカフェ教えて"
//   node scripts/node_rag_client.js rag "温泉"

const fetch = require('node-fetch');

/**
 * 통합 채팅 엔드포인트 (권장)
 * 자동으로 의도를 파악하고 적절히 응답합니다.
 */
async function chat(opts = {}) {
  const {
    host = 'http://localhost:8000',
    text,
    session_id = 'default-session',
  } = opts;

  if (!text) throw new Error('text is required');

  const body = { text, session_id };

  const res = await fetch(`${host}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`Server error ${res.status}: ${txt}`);
  }

  return res.json();
}

/**
 * RAG 검색 엔드포인트 (고급 제어용)
 * 직접 파라미터를 제어하여 검색합니다.
 */
async function queryRag(opts = {}) {
  const {
    host = 'http://localhost:8000',
    question,
    top_k = 5,
    domain = null,
    area = null,
    expansion = false,
    expansion_variations = null,
    parent_context = true,
  } = opts;

  if (!question) throw new Error('question is required');

  const body = {
    question,
    top_k,
    domain,
    area,
    expansion,
    expansion_variations,
    parent_context,
  };

  const res = await fetch(`${host}/rag/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`Server error ${res.status}: ${txt}`);
  }

  return res.json();
}

// CLI example
if (require.main === module) {
  const args = process.argv.slice(2);
  const mode = args[0] || 'chat'; // 'chat' or 'rag'
  const input = args[1] || 'こんにちは';

  (async () => {
    try {
      if (mode === 'chat') {
        console.log(`[통합 채팅] "${input}"`);
        const resp = await chat({ text: input, session_id: 'cli-session' });
        console.log(JSON.stringify(resp, null, 2));
        
        // 응답 타입별 간단 출력
        console.log('\n--- 요약 ---');
        console.log('타입:', resp.response_type);
        if (resp.response_type === 'search') {
          console.log('장소 수:', resp.places?.length || 0);
        } else if (resp.response_type === 'itinerary') {
          console.log('일정:', resp.itinerary?.title);
        }
      } else {
        console.log(`[RAG 검색] "${input}"`);
        const resp = await queryRag({ question: input, top_k: 3, expansion: true });
        console.log(JSON.stringify(resp, null, 2));
      }
    } catch (e) {
      console.error('에러:', e.message);
      process.exit(1);
    }
  })();
}

module.exports = { chat, queryRag };
