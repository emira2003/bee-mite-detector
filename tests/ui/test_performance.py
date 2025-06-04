import sqlite3

def test_average_fps_per_session():
    conn = sqlite3.connect("bee_health.db")
    cursor = conn.cursor()

    # Calculate average FPS for each session
    cursor.execute("""
        SELECT session_id, 
               ROUND(AVG(fps), 2) as avg_fps,
               ROUND(MIN(fps), 2) as min_fps,
               ROUND(MAX(fps), 2) as max_fps,
               COUNT(*) as total_frames
        FROM bee_metrics
        WHERE fps IS NOT NULL
        GROUP BY session_id
        ORDER BY session_id DESC
        LIMIT 5
    """)
    
    results = cursor.fetchall()
    conn.close()

    # Print results for your report
    print("\n Performance Testing Summary (Last 5 Sessions):")
    for row in results:
        print(f"Session {row[0]}: Avg FPS = {row[1]}, Min FPS = {row[2]}, Max FPS = {row[3]}, Frames = {row[4]}")

    assert results, "No sessions with FPS data found"
