# PySpective - An Open-Source Tool for Processing Spectroscopic Data

The analysis of spectroscopic data is an essential part of research and education in chemistry. Commercial software is often used for this purpose. For reasons of cost, however, there are not always sufficient licenses available for education, or the software license is bound to the hardware of the spectrometer. 
The use of open-source software, such as the ubiquitous programming language Python, represents an alternative to the use of commercial software. However, programming is not reasonable for all users, which is why a user-friendly software solution is needed. Some solutions for special measurement data already exist: [NMRium](https://www.nmrium.org/) and [ssNake](https://www.ru.nl/science/magneticresonance/software/ssnake/) for NMR spectroscopy, [ProteoWizard](https://proteowizard.sourceforge.io/) for mass spectrometry and [SupraFit](https://github.com/conradhuebler/SupraFit) for model fitting, among others.

PySpective is made for the evaluation of spectroscopic data, such as IR, Raman, UV/VIS and XRF spectroscopy. It is written in Python and can therefore be used platform-independently and without licensing problems. Due to its status as an open-source project, extensions and enhancement requests by users can be implemented by a community of developers. The recommendations of [NFDI4Chem](https://knowledgebase.nfdi4chem.de/knowledge_base/docs/synthetic_chemistry/) are implemented.

## Requirements

Python 3.x with packages:

- PyQt6
- matplotlib
- numpy
- scipy
- json

## Features

### File Formats:

Import:

- JCAMP-DX (currently without data compression)
- Import as a new document, a new page in the current document, or a new spectrum in the current plot
- text format (e.g. CSV) with options

Export:

- JCAMP-DX (currently without data compression)
- document, page, or spectrum can be saved separately (using the LINK block)
- display options (color, marker style, line style, ...) saved as user-defined labels

### Data Oragnisation

A document may consist of multiple pages with multiple spectra per page. So, for example, all the data for one compound can be saved in one document. The export of one page or one spectrum is also possible.

## Display Options

- document: title
- pages: title of plot, label of axes
- plots: color, line style, marker style

### Image Export

- to all file formats, matplotlib supports

### Metadata

- all metadata of JCAMP-DX
- Improvements planned (e. g. WISWESSER -> INCHI)

### Data Processing

- peak picking
- Numerical integration
- Numerical differentiation

## To Do:

- add all JCAMP-DX Features
- more import file formats, like:
  - spa
  - ...
- other data types like
  - XRF
  - NMR
  - Chromatograms
  - ...
- Bug fixing (of course)

## How can I help?

Contact me so we can start developing this app together.
