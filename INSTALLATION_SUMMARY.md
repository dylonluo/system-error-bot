System boto3 -> AWS S3 bucket -> list each pdf files and extract text using pypdf, generate presigned URL for document access

pdf reader extract text page by page, cleans up whitespace and special character

splits the documents into searchable chunks. then use keyword-based scoring. 

when the query comes in, search the chunks and find the top 10 most relevant chunks across all documents, and then rank the documents sort by total relevance score. 


RAG pipeline
User Query
    ↓
Intent Detection (is it on-topic?)
    ↓
Document Search (find relevant chunks)
    ↓
Get RAG Context (extract top 3 docs' content, ~4000 chars each)
    ↓
Build Prompt (query + context + conversation history)
    ↓
AI Provider (Bedrock Claude) generates response
    ↓
Return response + documentation links
      