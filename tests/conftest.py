# vim: set et sw=4 sts=4 fileencoding=utf-8:
#
# Python camera library for the Rasperry-Pi camera module
# Copyright (c) 2013,2014 Dave Hughes <dave@waveform.org.uk>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the copyright holder nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from __future__ import (
    unicode_literals,
    print_function,
    division,
    absolute_import,
    )

# Make Py2's str equivalent to Py3's
str = type('')

import picamera
import pytest


# The basic camera fixture returns a camera which is not running a preview.
# This should be used for tests which cannot be run when a preview is active
@pytest.fixture(scope='module')
def camera(request):
    camera = picamera.PiCamera()
    def fin():
        camera.close()
    request.addfinalizer(fin)
    return camera

# Activates and deactivates preview mode to test things in both states
@pytest.fixture(scope='module', params=(False, True))
def previewing(request, camera):
    if request.param and not camera.previewing:
        camera.start_preview()
    if not request.param and camera.previewing:
        camera.stop_preview()
    def fin():
        if camera.previewing:
            camera.stop_preview()
    request.addfinalizer(fin)
    return request.param

# Run tests at a variety of resolutions (and aspect ratios, 1:1, 4:3, 16:9) and
# framerates (which dictate the input mode of the camera)
@pytest.fixture(scope='module', params=(
    ((100, 100), 60),
    ((320, 240), 30),
    ((1280, 720), 30),
    ((1920, 1080), 24),
    ((2592, 1944), 15),
    ))
def mode(request, camera):
    save_resolution = camera.resolution
    save_framerate = camera.framerate
    camera.resolution, camera.framerate = request.param
    def fin():
        try:
            for port in camera._encoders:
                camera.stop_recording(splitter_port=encoder)
        finally:
            camera.resolution = save_resolution
            camera.framerate = save_framerate
    request.addfinalizer(fin)
    return request.param


