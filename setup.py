from setuptools import setup

def main():
    """
    setup the package

    """
    setup(
        packages=["src/iolite"],
        scripts=["bin/radial_average_bg",
                 "bin/ice_rings"],
        install_requires=[],
        setup_requires=["pytest-runner"],
        tests_require=["pytest", "pytest-cov", "mock"],
        test_suite="tests",
        extras_require={"build_sphinx": ["sphinx", "sphinx_rtd_theme"]},
    )


if __name__ == "__main__":
    main()
