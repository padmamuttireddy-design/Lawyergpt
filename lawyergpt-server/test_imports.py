import sys, os
# simulate what the server does
engine_path = "C:\\ProjectsLive\\LawyerGPT\\lawyergpt-engine"
sys.path.insert(0, engine_path)

print("sys.path entries:", sys.path[:5])

# directly replicate the lazy import that fails
try:
    from langchain_openai import OpenAIEmbeddings
    print("langchain_openai OK from engine-path sys.path")
except ImportError as e:
    print("langchain_openai FAIL:", e)

# also test chromadb
try:
    import chromadb
    print("chromadb OK:", chromadb.__version__)
except ImportError as e:
    print("chromadb FAIL:", e)
