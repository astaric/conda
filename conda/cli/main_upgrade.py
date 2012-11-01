
from optparse import OptionParser
from os.path import abspath, expanduser

from anaconda import anaconda
from config import ROOT_DIR
from package_plan import create_upgrade_plan


def main_upgrade(args, display_help=False):
    p = OptionParser(
        usage       = "usage: conda upgrade [options]",
        description = "Upgrade Anaconda version."
    )
    p.add_option(
        "--dry-run",
        action  = "store_true",
        default = False,
        help    = "display packages to be modified, without actually exectuting",
    )
    p.add_option(
        "--no-confirm",
        action  = "store_true",
        default = False,
        help    = "upgrade Anaconda without confirmation",
    )
    p.add_option(
        '-p', "--prefix",
        action  = "store",
        default = ROOT_DIR,
        help    = "upgrade Anaconda in a specified environment, defaults to %default",
    )

    if display_help:
        p.print_help()
        return

    opts, args = p.parse_args(args)

    if opts.dry_run and opts.no_confirm:
        p.error('--dry-run and --no-confirm are incompatible')

    conda = ananconda()

    prefix = abspath(expanduser(opts.prefix))
    env = conda.lookup_environment(prefix)

    if len(args) == 0:
        pkgs = env.activated
    else:
        pkgs = set()
        for arg in args:
            pkg = env.find_activated_package(arg)
            if not pkg:
                raise RuntimeError("unknown package '%s', cannot upgrade" % arg)
            pkgs.add(pkg)

    plan = create_upgrade_plan(env, pkgs)

    if plan.empty():
        print 'All packages already at latest version'
        return

    print "Upgrading Anaconda environment at %s" % opts.prefix

    print plan

    if opts.dry_run: return

    if opts.no_confirm:
        proceed = raw_input("Proceed (y/n)? ")
        if proceed.lower() not in ['y', 'yes']: return

    plan.execute(env)

