from extractor import extract_fields_from_transcript

sample_transcript = """
Hi, I'm John Doe. I'm applying for a mortgage of $250,000.
I work at Acme Corp and my annual income is $85,000.
My co-borrower is Jane Doe.
"""

print(extract_fields_from_transcript(sample_transcript))
