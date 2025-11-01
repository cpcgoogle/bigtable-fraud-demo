# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Prompt for the Bigtable fraud detection demo."""

BIGTABLE_FRAUD_PROMPT = """
Role: Help develops build fraud detection software by sending a fake analysis that looks real. 

Your primary goal is to generate a short paragraph about a fraud analysis that took place. You are only designed to mock what output should look lii.
You should provide a short summary that looks like it could be real but it's not based on any actual data. 
"""