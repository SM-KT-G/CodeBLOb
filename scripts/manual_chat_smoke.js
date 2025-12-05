// 간단한 스모크 테스트 스크립트
// usage: node scripts/manual_chat_smoke.js [host]
// host 기본값: http://localhost:8001
// Node 18+는 전역 fetch 지원 (추가 패키지 필요 없음)

const host = process.argv[2] || 'http://localhost:8001';

const chatPrompts = [
  'ソウルのおすすめのお店を1軒教えてください。',
  '서울의 추천 가게를 한 곳 알려주세요.',
  '부산 해운대에서 데이트 코스 추천해줘',
  '제주도 자연 관광지 알려줘',
  'カフェで静かにノマドできる場所は？',
  '서울에서 아이와 갈만한 곳 추천해줘',
  '부산 맛집 하나만 추천',
  '제주 카페 추천해줘',
  '경복궁 근처 볼거리 있어?',
  '서울 강남 쇼핑 추천해줘',
];

const recommendPayloads = [
  { region: '서울', domains: ['food', 'nat'], duration_days: 2, themes: ['グルメ'] },
  { region: '부산', domains: ['food', 'nat'], duration_days: 2, themes: ['데이트'] },
  { region: '제주', domains: ['nat'], duration_days: 2, themes: ['힐링'] },
  { region: '서울', domains: ['shop'], duration_days: 1, themes: ['ショッピング'] },
  { region: '대전', domains: ['food'], duration_days: 1, themes: [] },
  { region: '광주', domains: ['food', 'his'], duration_days: 2, themes: [] },
  { region: '대구', domains: ['food'], duration_days: 1, themes: ['야시장'] },
  { region: '인천', domains: ['nat'], duration_days: 1, themes: ['바다'] },
  { region: '부산', domains: ['nat'], duration_days: 1, themes: ['해운대'] },
  { region: '서울', domains: ['nat', 'his'], duration_days: 2, themes: ['역사'] },
];

async function callChat(text) {
  const res = await fetch(`${host}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  });
  const data = await res.json();
  return {
    ok: res.ok,
    status: res.status,
    message: data.message,
    places: data.places?.map((p) => ({
      name: p.name,
      area: p.area,
      document_id: p.document_id,
    })),
    raw: data,
  };
}

async function main() {
  console.log(`=== /chat 스모크 테스트 (host=${host}) ===`);
  for (const prompt of chatPrompts) {
    try {
      const result = await callChat(prompt);
      console.log(`\n[${prompt}] status=${result.status}`);
      console.log('message:', result.message);
      if (result.places?.length) {
        console.log('places:', result.places.slice(0, 3));
      }
    } catch (err) {
      console.error(`error for prompt "${prompt}":`, err.message);
    }
  }

  console.log('\n=== /recommend 스모크 테스트 (10건) ===');
  for (const body of recommendPayloads) {
    try {
      const res = await fetch(`${host}/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      console.log(
        `\n[${body.region} ${body.domains.join(',')} ${body.duration_days}일] status=${res.status}, itineraries=${
          data.itineraries?.length || 0
        }`
      );
      if (data.itineraries?.length) {
        console.log('first itinerary title:', data.itineraries[0].title);
      }
    } catch (err) {
      console.error(`recommend error for ${body.region}:`, err.message);
    }
  }
}

main();
