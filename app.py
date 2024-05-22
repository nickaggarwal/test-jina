import json
import numpy as np
import torch
from transformers import pipeline
class InferlessPythonModel:
    def initialize(self):
        try:
            self.generator = pipeline(
                "feature-extraction",
                model="jinaai/jina-reranker-v1-turbo-en",
                device=0,
                ignore_mismatched_sizes=True
            )
            print("Pipeline initialized successfully.")
        except Exception as e:
            print(f"Error initializing pipeline: {e}")
            self.generator = None
    def infer(self, input_data):
        if isinstance(input_data, dict):
            input_json = input_data
        else:
            input_json = json.loads(input_data)
        query = input_json['query']
        chunks = input_json['chunks']
        if not isinstance(chunks, list) or not all(isinstance(chunk, str) for chunk in chunks):
            raise ValueError("Chunks must be a list of strings")
        combined_input = [f"{query} {chunk}" for chunk in chunks]
        results = self.generator(combined_input)
        print("Results structure:", results)
        for i in range(len(results)):
            print(f"Result {i}: {results[i]}")
            if isinstance(results[i], list) and len(results[i]) > 0 and isinstance(results[i][0], dict):
                results[i][0]['text'] = chunks[i]
            else:
                print(f"Unexpected result format at index {i}: {results[i]}")
        try:
            ranked_results = sorted(results, key=lambda x: x[0]['score'], reverse=True)
        except (TypeError, KeyError, IndexError) as e:
            print(f"Error during sorting: {e}")
            ranked_results = results
        result_texts = []
        for result in ranked_results:
            if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict) and 'text' in result[0]:
                result_texts.append(str(result[0]['text']))
            else:
                print(f"Unexpected result format: {result}")
        return {"result": result_texts}
    def finalize(self):
        self.generator = None
        print("Pipeline finalized.")