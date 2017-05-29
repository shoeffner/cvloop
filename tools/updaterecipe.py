import sys


def main():
    recipe_filename = './tools/cvloop-feedstock/recipe/meta.yaml'
    with open(recipe_filename) as recipe_file:
        recipe = recipe_file.read().splitlines()

    recipe[1] = '{{% set version = "{}" %}}'.format(sys.argv[1])
    recipe[2] = '{{% set sha256 = "{}" %}}'.format(sys.argv[2])

    with open(recipe_filename, 'w') as recipe_file:
        print(*recipe, sep='\n', file=recipe_file)


if __name__ == '__main__':
    main()
