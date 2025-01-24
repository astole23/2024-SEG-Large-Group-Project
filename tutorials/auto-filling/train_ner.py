import spacy
from spacy.training import Example
from training_data import TRAINING_DATA

def train_ner():
    # Load a blank English NLP model
    nlp = spacy.blank("en")
    
    # Add a new NER pipeline
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner", last=True)
    
    # Add labels to the NER model
    for _, annotations in TRAINING_DATA:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])
    
    # Convert training data into spaCy's Example format
    examples = []
    for text, annotations in TRAINING_DATA:
        examples.append(Example.from_dict(nlp.make_doc(text), annotations))
    
    # Start training
    optimizer = nlp.begin_training()
    for epoch in range(20):  # You can adjust the number of epochs
        losses = {}
        nlp.update(examples, drop=0.5, losses=losses)
        print(f"Epoch {epoch}: Losses {losses}")
    
    # Save the trained model to disk
    nlp.to_disk("./ner_model")
    print("Model saved to ./ner_model!")

if __name__ == "__main__":
    train_ner()
