python -m src.ingestion.fetch_and_transcribe_200  # Step 1: Fetch & transcribe only new videos
python -m src.preprocess.process_transcripts      # Step 2: Process transcripts (clean & chunk)
python -m src.embeddings.embedder                 # Step 3: Embed only new transcripts
python -m src.query.query_engine                  # Step 4: Query updated database