from pipeline.retriever import build_query_engine

engine = build_query_engine()
response = engine.query("What is the main title of Chapter 6 of the Trademarks Act 2019")
print(response.response)
print("\n--- Sources used ---")
for node in response.source_nodes:
    print(f"{node.score:.4f} | {node.node.metadata.get('headings')}")