import json
import tiktoken

# Cargar archivo JSON con los datos
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Contar tokens en el texto usando tiktoken
def count_tokens(text, tokenizer):
    return len(tokenizer.encode(text))

# Procesar el archivo y contar los tokens en prompt y completion
def analyze_token_counts(data, tokenizer, totaltokensenunprompt ):
    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_entries = len(data)
    
    for entry in data:
        prompt = entry['prompt']
        completion = entry['completion']
        
        prompt_tokens = count_tokens(prompt, tokenizer)
        completion_tokens = count_tokens(completion, tokenizer)

        total_prompt_tokens += prompt_tokens
        total_completion_tokens += completion_tokens
        if totaltokensenunprompt < (prompt_tokens + completion_tokens ):
            totaltokensenunprompt = prompt_tokens + completion_tokens

        print(f"Prompt Tokens: {prompt_tokens}, Completion Tokens: {completion_tokens} - Total: {prompt_tokens + completion_tokens}")

    print(f"\nTotal Prompts: {total_entries}")
    print(f"Total Prompt Tokens: {total_prompt_tokens}")
    print(f"Total Completion Tokens: {total_completion_tokens}")
    print(f"Average Prompt Tokens: {total_prompt_tokens / total_entries}")
    print(f"Average Completion Tokens: {total_completion_tokens / total_entries}")
    print(f"Total maxi tokens en un prompt: {totaltokensenunprompt}")

# Ruta al archivo JSON
json_file_path = 'corridos_dataset.json'
totaltokensenunprompt = 0
# Cargar el JSON
data = load_json(json_file_path)

# Elegir el tokenizador (ejemplo con GPT-3)
tokenizer = tiktoken.get_encoding('cl100k_base')

# Analizar y contar los tokens
analyze_token_counts(data, tokenizer,totaltokensenunprompt)
