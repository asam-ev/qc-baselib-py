from typing import Annotated, Union, List
from pydantic import Field, BaseModel
from pydantic_xml import BaseXmlModel, attr, element


# Common types for both schemas
class ParamType(BaseXmlModel, tag="Param"):
    name: Annotated[str, Field(min_length=1)] | None = attr(name="name")
    value: Annotated[Union[str, int, float], Field()] | None = attr(
        name="value", default_factory=str
    )
