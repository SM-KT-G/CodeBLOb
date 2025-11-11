// Simple Node.js wrapper for calling the FastAPI RAG backend
// Usage: node scripts/node_rag_client.js

const fetch = require('node-fetch');

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
  (async () => {
    try {
      const resp = await queryRag({ question: '温泉', top_k: 3, domain: 'stay', expansion: true });
      console.log(JSON.stringify(resp, null, 2));
    } catch (e) {
      console.error(e);
      process.exit(1);
    }
  })();
}

module.exports = { queryRag };
