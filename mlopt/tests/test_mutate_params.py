# coding: utf-8
from . import TestCase, main
from mlopt.resources.llvm_config import llvm_opt_options
from mlopt.params import Params


class TestParams(TestCase):

    def test_mutate(self):
        para = Params()
        para.load(llvm_opt_options)

        for key, param in para._storage.items():
            if "(bool)" == param.ttype:
                para._storage[key] = param._replace(value="true")

        print(" ".join(para.to_cmd_args()))


if __name__ == '__main__':
    main()
