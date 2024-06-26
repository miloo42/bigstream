import argparse
import numpy as np
import bigstream.io_utility as io_utility

from bigstream.transform import apply_transform


def _inttuple(arg):
    if arg is not None and arg.strip():
        return tuple([int(d) for d in arg.split(',')])
    else:
        return ()


def _stringlist(arg):
    if arg is not None and arg.strip():
        return list(filter(lambda x: x, [s.strip() for s in arg.split(',')]))
    else:
        return []


def _define_args():
    args_parser = argparse.ArgumentParser(description='Apply transformation')
    args_parser.add_argument('--fixed', dest='fixed',
                             required=True,
                             help='Path to the fixed image')
    args_parser.add_argument('--fixed-subpath',
                             dest='fixed_subpath',
                             help='Fixed image subpath')

    args_parser.add_argument('--moving', dest='moving',
                             required=True,
                             help='Path to the moving image')
    args_parser.add_argument('--moving-subpath',
                             dest='moving_subpath',
                             help='Moving image subpath')

    args_parser.add_argument('--affine-transformations',
                             dest='affine_transformations',
                             type=_stringlist,
                             help='Affine transformations')

    args_parser.add_argument('--output',
                             dest='output',
                             required=True,
                             help='Output directory')
    args_parser.add_argument('--output-subpath',
                             dest='output_subpath',
                             help='Subpath for the transformed output')
    args_parser.add_argument('--output-chunk-size',
                             dest='output_chunk_size',
                             default=128,
                             type=int,
                             help='Output chunk size')
    args_parser.add_argument('--output-blocksize',
                             dest='output_blocksize',
                             type=_inttuple,
                             help='Output chunk size as a tuple.')

    return args_parser


def _run_apply_transform(args):

    # Read the highres inputs - if highres is not defined default it to lowres
    fix_subpath = args.fixed_subpath
    mov_subpath = args.moving_subpath if args.moving_subpath else fix_subpath
    output_subpath = args.output_subpath if args.output_subpath else mov_subpath

    fix_data, fix_attrs = io_utility.open(args.fixed, fix_subpath)
    mov_data, mov_attrs = io_utility.open(args.moving, mov_subpath)
    fix_voxel_spacing = io_utility.get_voxel_spacing(fix_attrs)
    mov_voxel_spacing = io_utility.get_voxel_spacing(mov_attrs)

    print('Fixed volume attributes:',
          fix_data.shape, fix_voxel_spacing, flush=True)
    print('Moving volume attributes:',
          mov_data.shape, mov_voxel_spacing, flush=True)

    if (args.output_blocksize is not None and
        len(args.output_blocksize) > 0):
        output_blocksize = args.output_blocksize
    else:
        # default to output_chunk_size
        output_blocksize = (args.output_chunk_size,) * fix_data.ndim

    if args.output:
        if args.affine_transformations:
            transforms_list = [np.loadtxt(tfile)
                               for tfile in args.affine_transformations]
        else:
            transforms_list = []

        transformed = apply_transform(
            fix_data, mov_data,
            fix_voxel_spacing, mov_voxel_spacing,
            transform_list=transforms_list
        )

        output_dataset = io_utility.create_dataset(
            args.output,
            output_subpath,
            fix_data.shape,
            output_blocksize,
            fix_data.dtype,
            data=transformed
        )

        return output_dataset
    else:
        return None


if __name__ == '__main__':
    args_parser = _define_args()
    args = args_parser.parse_args()
    print('Invoked transformation:', args, flush=True)

    _run_apply_transform(args)
