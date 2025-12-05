#!/bin/bash
# 임베딩 진행 상황 실시간 모니터링

while true; do
    clear
    echo "======================================"
    echo "📊 v1.1 임베딩 진행 상황"
    echo "======================================"
    echo ""
    
    # 로그에서 최신 진행률 추출
    echo "🔄 처리 진행:"
    tail -1 /Users/ckdlsxor/Desktop/Training/embedding_v1.1.log | grep -o "[0-9]*%\|[0-9]*/[0-9]*\|[0-9.]*it/s\|[0-9:]*<[0-9:]*" | sed 's/^/   /'
    echo ""
    
    # 프로세스 상태
    echo "⚡ 프로세스 상태:"
    ps aux | grep embed_initial_data_v1.1.py | grep -v grep | awk '{printf "   PID: %s | CPU: %s%% | MEM: %.1fGB\n", $2, $3, $6/1024/1024}'
    echo ""
    
    # DB 통계
    echo "💾 DB 저장 현황:"
    PGPASSWORD=tourism_pass psql -h localhost -U tourism_user -d tourism_db -t -A -c "
        SELECT 'Parents: ' || COUNT(*) FROM tourism_parent;
        SELECT 'Children: ' || COUNT(*) FROM tourism_child;
        SELECT 'Avg QA/Doc: ' || ROUND(CAST(COUNT(*) AS NUMERIC) / NULLIF((SELECT COUNT(*) FROM tourism_parent), 0), 1) FROM tourism_child;
    " 2>/dev/null | sed 's/^/   /'
    echo ""
    
    # 체크포인트 파일 확인
    if [ -f /Users/ckdlsxor/Desktop/Training/scripts/embedding_checkpoint_v1.1.json ]; then
        echo "📁 체크포인트 정보:"
        cat /Users/ckdlsxor/Desktop/Training/scripts/embedding_checkpoint_v1.1.json | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"   총 Parents: {data.get('total_parents', 0):,}개\")
print(f\"   총 Children: {data.get('total_children', 0):,}개\")
print(f\"   마지막 업데이트: {data.get('last_updated', 'N/A')[:19]}\")
" 2>/dev/null
        echo ""
    fi
    
    echo "======================================"
    echo "새로고침: 10초마다 (Ctrl+C로 종료)"
    echo "======================================"
    
    sleep 10
done
