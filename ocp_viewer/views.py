"""The two HTTP routes: the page, and a redirect to it."""

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

from flask import Blueprint, current_app, redirect, render_template, request

bp = Blueprint("viewer", __name__)


def viewer():
    """The running viewer, off the app that holds it."""
    return current_app.extensions["ocp_viewer"]


@bp.route("/")
def root():
    return redirect("/viewer", code=302)


@bp.route("/viewer")
def page():
    v = viewer()
    # The websocket address is taken from the request rather than from how this
    # server was started: a browser may have reached it by a hostname that is
    # routable from where it is, and that is the address it must dial back.
    #
    # partition rather than split, because the Host header carries no port when
    # the port is the scheme's default - behind a proxy, or on 80. An empty
    # port is what comms.js already treats as "the default one"; splitting on
    # ":" raised instead.
    address, _, port = request.host.partition(":")
    return render_template(
        "viewer.html",
        ws_host=address,
        ws_port=port,
        max_retries=(
            "" if v.max_reconnect_attempts is None else v.max_reconnect_attempts
        ),
        treeWidth=v.config["tree_width"],
        **v.config,
    )
