from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


# Defines a Pydantic model to structure the output data
class DocumentIntel(BaseModel):
    summary: str = Field(
        description="gives a summary of the document sent for analysis"
    )
    interesting_fact: str = Field(
        description="points out a interesting fact of the document sent for analysis"
    )

    # Defines a method to convert the model instance to a dictionary for easier processing
    def to_dict(self):
        return {
            "summary": self.summary,
            "interesting_fact": self.interesting_fact
        }


# Create a parser instance to convert output data into ReviewIntel model instances
document_intel_parser: PydanticOutputParser = PydanticOutputParser(pydantic_object=DocumentIntel)
