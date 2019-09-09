from setuptools import setup


def main():
    """
    setup the package

    """
    setup(
        packages=["src/iolite"],
        scripts=[
            "bin/radial_average_bg",
            "bin/ice_rings",
            "bin/classify_sigma",
            "bin/classify_overlaps",
            "bin/overlapping_spots",
            "bin/label_dataset",
            "bin/plot_results_overlaps",
            "bin/sigma_values",
            "bin/iolite_preparation"
        ],
        install_requires=[],
        setup_requires=["pytest-runner"],
        tests_require=["pytest", "pytest-cov", "mock"],
        test_suite="tests",
        extras_require={"build_sphinx": ["sphinx", "sphinx_rtd_theme"]},
    )


if __name__ == "__main__":
    main()
