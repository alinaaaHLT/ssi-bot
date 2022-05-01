default_text_generation_parameters = {
#		'max_length': 1024,
		'max_new_tokens': 250, # inference API limits tokens, not words
		'num_return_sequences': 1,
		'prompt': None,
		'temperature': 0.8,
		'top_k': 40,
		'repetition_penalty': 1.008,
		'stop_token': '<|endoftext|>', # I hope there is stop token but I don't think so
}

from .model_text_generator import ModelTextGenerator
