from icecream import ic
from icecream import install
import argparse
import logging
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")


def inputParameters():
    parser = argparse.ArgumentParser()
    parser.description = "please enter some parameters"
    parser.add_argument(
        "-d",
        "--debug",
        help="是否打印Debug信息 is print debug informations",
        dest="debug",
        type=str,
        choices=["yes", "no"],
        default="no",
    )
    parser.add_argument(
        "-p",
        "--path",
        help="包括failed和 JAV_output文件夹的根文件夹",
        dest="path",
        type=str,
        required=True
    )

    args = parser.parse_args()

    log.info("parameter debug is : %s " % args.debug)
    log.info("parameter path is : %s " % args.path)
    print("")
    return args

def isIceEnable(isYes):
    install()
    ic.configureOutput(prefix='Debug -> ')
    if isYes=="yes" : 
        ic.enable()
    else:
        ic.disable()