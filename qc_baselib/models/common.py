# Copyright 2024, ASAM e.V.
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import Annotated, Union
from pydantic import Field
from pydantic_xml import BaseXmlModel, attr


# Common types for both schemas
class ParamType(BaseXmlModel, tag="Param"):
    name: Annotated[str, Field(min_length=1)] | None = attr(name="name")
    value: Annotated[Union[str, int, float], Field()] | None = attr(
        name="value", default_factory=str
    )
