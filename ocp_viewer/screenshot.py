"""Writing a screenshot the browser sent back as a data URL."""

#
# Copyright 2026 Bernhard Walter
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import base64
import shutil
import time


def save_png_data_url(data_url, output_path):
    """Write the image, under a temporary name first.

    A caller polls for the file to appear, so a partly written one would be
    picked up as a finished one. Writing beside it and renaming means the
    file exists only once it is complete.
    """
    image_data = base64.b64decode(data_url.split(",")[1])
    suffix = "-temp" + hex(int(time.time() * 1e6))[2:]
    try:
        with open(output_path + suffix, "wb") as f:
            f.write(image_data)
        shutil.move(output_path + suffix, output_path)
        print(f"Wrote png file to {output_path}")
    except Exception as ex:  # noqa: BLE001
        print("Cannot save png file:", str(ex))
