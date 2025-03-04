from pathlib import PurePath
from shutil import which
from subprocess import DEVNULL, PIPE, CalledProcessError, check_call
from typing import Sequence, Union, cast

from pynvim import Nvim
from pynvim_pp.api import get_cwd
from pynvim_pp.lib import threadsafe_call, write
from pynvim_pp.logging import log

from ..fs.types import Node
from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.types import State
from .shared.index import indices


def _open_gui(path: PurePath, cwd: PurePath) -> None:
    if cmd := which("open"):
        command: Sequence[Union[PurePath, str]] = (cmd, "--", path)
    elif cmd := which("xdg-open"):
        command = (cmd, path)
    elif cmd := which("start"):
        command = (cmd, path)
    else:
        raise LookupError(LANG("sys_open_err"))

    check_call(command, stdin=DEVNULL, stdout=PIPE, stderr=PIPE, cwd=cwd)


@rpc(blocking=False)
def _open_sys(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> None:
    """
    Open using finder / dolphin, etc
    """

    node = next(indices(nvim, state=state, is_visual=is_visual), None)
    if not node:
        return None
    else:
        cwd = get_cwd(nvim)

        def cont() -> None:
            try:
                _open_gui(cast(Node, node).path, cwd=cwd)
            except (CalledProcessError, LookupError) as e:
                threadsafe_call(nvim, write, nvim, e, error=True)
            except Exception as e:
                log.exception("%s", e)

        state.pool.submit(cont)
