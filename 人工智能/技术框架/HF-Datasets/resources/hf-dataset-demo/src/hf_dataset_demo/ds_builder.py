"""
@File: ds_builder.py
@Author: Meimin Wang
@Date: 2025/11/20 16:51
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
from typing import Union

from datasets import GeneratorBasedBuilder, DownloadManager, StreamingDownloadManager, DatasetInfo, Features, Value, \
    ClassLabel, SplitGenerator

data = [
    {'text': 'This is a negative example.', 'label': 'negative'},
    {'text': 'This is a positive example.', 'label': 'positive'},
    {'text': 'This is another negative example.', 'label': 'negative'},
    {'text': 'This is yet another positive example.', 'label': 'positive'},
    {'text': 'This is a third negative example.', 'label': 'negative'},
    {'text': 'This is a fourth positive example.', 'label': 'positive'},
    {'text': 'This is a fifth negative example.', 'label': 'negative'},
    {'text': 'This is a sixth positive example.', 'label': 'positive'},
]

class MyDatasetBuilder(GeneratorBasedBuilder):
    def _generate_examples(self, **kwargs):
        for i, row in enumerate(data):
            yield i, row

    def _info(self) -> DatasetInfo:
        return DatasetInfo(
            description="This is a description of my dataset.",
            homepage="",
            license="MIT",
            features=Features(text=Value("string"), label=ClassLabel(names=["negative", "positive"])),
        )

    def _split_generators(self, dl_manager: Union[DownloadManager, StreamingDownloadManager]):
        return [
            SplitGenerator(name="train", gen_kwargs={}),
            SplitGenerator(name="test", gen_kwargs={}),
        ]