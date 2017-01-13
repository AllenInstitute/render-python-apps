import os
from renderapi import Render
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Delete Stack")
    parser.add_argument('--stackName', nargs=1, help='project directory', type=str)

    args = parser.parse_args()

    render = Render("ibs-forrestc-ux1.corp.alleninstitute.org", 8080, "Sharmishtaas", "M270907_Scnn1aTg2Tdt_13")
    render.delete_stack(args.stackName[0])
