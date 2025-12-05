#!/bin/bash
# v1.1 임베딩 진행 상황 모니터링

while true; do
    clear
    echo "==================== v1.1 임베딩 진행 상황 ===================="
    echo ""
    
    # 프로세스 상태
    echo "📊 프로세스 상태:"
    ps aux | grep embed_initial_data_v1.1.py | grep -v grep | awk '{printf "   PID: %s, CPU: %s%%, MEM: %s%%\n", $2, $3, $4}'
    
    # 로그 마지막 10줄
    echo ""
    echo "📝 최근 로그:"
    tail -10 /Users/ckdlsxor/Desktop/Training/embedding_v1.1.log | sed 's/^/   /'
    
    # DB 통계
    echo ""
    echo "🗄️  DB 통계:"
    PGPASSWORD=tourism_pass psql -h localhost -U tourism_user -d tourism_db -t -c "
        SELECT 
            'Parents: ' || COUNT(*) as count 
        FROM tourism_parent;
        
        SELECT 
            'Children: ' || COUNT(*) as count 
        FROM tourism_child;
    " 2>/dev/null | sed 's/^/   /'
    
    echo ""
    echo "========================================================"
    echo "새로고침: 30초마다 (Ctrl+C로 종료)"
    
    sleep 30
done
