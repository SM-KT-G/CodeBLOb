// Simple Node.js wrapper for calling the FastAPI RAG backend
// Usage: 
//   node scripts/node_rag_client.js chat "ソウルでおすすめのカフェ教えて"
//   node scripts/node_rag_client.js rag "温泉"

const fetch = require('node-fetch');

/**
 * 통합 채팅 엔드포인트 (대화/검색 전용)
 */
async function chat(opts = {}) {
  const {
    host = 'http://localhost:8000',
    text,
  } = opts;

  if (!text) throw new Error('text is required');

  const body = { text };

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

/**
 * 여행 일정 추천 엔드포인트
 * POST /recommend (alias of /recommend/itinerary)
 */
async function recommendItinerary(opts = {}) {
  const {
    host = 'http://localhost:8000',
    region,
    domains = [],
    duration_days,
    themes = [],
    transport_mode = null,
    budget_level = null,
  } = opts;

  if (!region) throw new Error('region is required');
  if (!domains.length) throw new Error('domains is required');
  if (!duration_days) throw new Error('duration_days is required');

  const body = {
    region,
    domains,
    duration_days,
    themes,
    transport_mode,
    budget_level,
  };

  const res = await fetch(`${host}/recommend`, {
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
  const mode = args[0] || 'chat'; // 'chat' or 'rag' or 'recommend'
  const input = args[1] || 'こんにちは';

  (async () => {
    try {
      if (mode === 'chat') {
        console.log(`[통합 채팅] "${input}"`);
        const resp = await chat({ text: input });
        console.log(JSON.stringify(resp, null, 2));
        if (resp.places?.length) {
          console.log('\n--- 장소 검색 결과 ---');
          console.log('장소 수:', resp.places.length);
        }
      } else if (mode === 'rag') {
        console.log(`[RAG 검색] "${input}"`);
        const resp = await queryRag({ question: input, top_k: 3, expansion: true });
        console.log(JSON.stringify(resp, null, 2));
      } else if (mode === 'recommend') {
        console.log(`[일정 추천] "${input}"`);
        const resp = await recommendItinerary({
          region: input,
          domains: ['food', 'nat'],
          duration_days: 2,
          themes: ['グルメ'],
        });
        console.log(JSON.stringify(resp, null, 2));
      }
    } catch (e) {
      console.error('에러:', e.message);
      process.exit(1);
    }
  })();
}

module.exports = { chat, queryRag, recommendItinerary };
