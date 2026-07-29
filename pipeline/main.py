Run python main.py
Traceback (most recent call last):
==================================================
  File "/home/runner/work/ai-/ai-/pipeline/main.py", line 152, in <module>
AI NEWS & DISCOVERY PIPELINE
==================================================
0 previously processed

    main()
FETCHING FROM ALL SOURCES...
Fetching from RSS feeds...
Fetching from Reddit...
Fetching from Hacker News...
Fetching from Product Hunt...
Total items collected: 72

RANKING WITH MISTRAL AI...
  File "/home/runner/work/ai-/ai-/pipeline/main.py", line 105, in main
    ranked_items = rank_with_mistral(all_items, count=total_needed)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/ai-/ai-/pipeline/main.py", line 40, in rank_with_mistral
    genai.configure(api_key=MISTRAL_API_KEY)
    ^^^^^
NameError: name 'genai' is not defined
Error: Process completed with exit code 1.
