"""
@File: demo_2.py
@Author: Meimin Wang
@Date: 2025/11/20 16:58
@Email: blessedwmm@gmail.com
@Email: wangmeimin@cstor.cn
@Description: 

Copyright (c) 2025 Meimin Wang
All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from datasets import load_dataset, load_dataset_builder

from hf_dataset_demo.ds_builder import MyDatasetBuilder

builder = MyDatasetBuilder()
builder.download_and_prepare()
ds = builder.as_dataset()
print(ds)