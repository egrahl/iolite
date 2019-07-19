from setuptools import setup

def main():
    """
    setup the package

    """
    setup(
        packages=["src/iolite"],
        scripts=["bin/make_radial_average"],
        install_requires=[],
        setup_requires=["pytest-runner"],
        tests_require=["pytest", "pytest-cov", "mock"],
        test_suite="tests",
        extras_require={"build_sphinx": ["sphinx", "sphinx_rtd_theme"]},
    )


if __name__ == "__main__":
    main()
