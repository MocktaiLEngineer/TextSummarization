from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import math
import evaluate

class ConversationSummarizer:
    def __init__(self, model, tokenizer, max_token_length=1024, overlap=10):
        self.tokenizer = tokenizer
        self.model = model
        self.max_token_length = max_token_length
        self.overlap = overlap

    def split_into_segments(self, conversation):
        conversation_tokens = self.tokenizer.tokenize(conversation)
        segments = []

        i = 0
        while i < len(conversation_tokens):
            segment = conversation_tokens[i:i+self.max_token_length]
            segments.append(self.tokenizer.convert_tokens_to_string(segment))
            i += self.max_token_length - self.overlap

        return segments

    def get_summary(self, conversation, max_length=150):
        conversation_tokens = self.tokenizer.encode(conversation, return_tensors='pt', max_length=self.max_token_length, truncation=True)
        num_segments = math.ceil(len(conversation_tokens[0]) / self.max_token_length)
        max_length_per_segment = max(max_length // num_segments, 30)  # Ensure max_length is not less than 30 (min_length)

        # Summarize the conversation
        summary_ids = self.model.generate(conversation_tokens, max_length=max_length_per_segment, min_length=30, length_penalty=2.0, num_beams=4, early_stopping=True)
        
        # Decode the summary and return it
        summary_text = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        
        return summary_text

    def summarize(self, conversation, max_length=150):
        # If the conversation is too long, we need to split it into segments
        if len(self.tokenizer.encode(conversation)) > self.max_token_length:
            segments = self.split_into_segments(conversation)
            max_length_per_segment = max_length // len(segments)  # adjust max_length based on number of segments

            summaries = []
            for segment in segments:
                segment_summary = self.get_summary(segment, max_length_per_segment)
                summaries.append(segment_summary)

            # Combine the segment summaries into a final summary
            final_summary = " ".join(summaries)
        else:
            # If the conversation is not too long, we can just summarize it directly
            final_summary = self.get_summary(conversation, max_length)

        return final_summary

    def summarize_to_points(self, conversation, max_length=50, num_points=3):
        summary = self.summarize(conversation, max_length=max_length * num_points)
        sentences = summary.split('. ')
        if len(sentences) > num_points:
            sentences = sentences[:num_points]
        return '\n'.join([f"- {sentence}" for sentence in sentences])

    def summarize_to_headline(self, conversation, max_length=30):
        summary = self.summarize(conversation, max_length=max_length)
        return summary.split('. ')[0]

    def evaluate(self, summaries, references):
        rouge_score = evaluate.load("rouge")

        return rouge_score.compute(predictions=summaries, references=references)