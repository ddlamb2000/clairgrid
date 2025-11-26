# clairgrid

PROOF OF CONCEPT

Currently, clairgrid is an experimental web application focused on data management.

The research behind clairgrid aims to develop a robust engine for data structuring, relationship management, presentation, and, most importantly, intuitive data navigation.

This innovative application requires no database knowledge or skills, as all aspects are managed in real time through a simple, web-based user interface.

Primarily designed for small businesses, the application enables the management of diverse and extensive organizational information, facilitating easy and natural sharing among stakeholders using only a web browser.

εncooη also serves as the foundation for developing a comprehensive business-oriented application development toolkit.

Copyright David Lambert 2025

# Techstack

1. Docker: https://www.docker.com/
1. Postgresql: https://www.postgresql.org/

# History

2007 - Project factory (https://sourceforge.net/projects/projectfactory/). As an open source project for project management, Factory lets you organize actors in teams, define projects, create version-based plans, generate forecast calendars and track statuses. Small and stand alone, it runs on every system with Java.

2012 - Prototype using Ruby on Rails and sqlite3 . First attenpt to make somthing entirely generic and dynamic. The implementation of row-level security came very late and turned to be impossible to make.

2022 - Prototype using Docker, Go, Go-gin, React and Postgreqsl. Adopting Go was great, but React wasn't. The code for the UI was a mess. The traditional approach as a monolith was a mistake.

2025 - Prototype using Docker, Go, Kafka, Postgreqsl and Svelte. Adoption an event-based architecture using Kafka. Svelte is sweet.


# Notes for developers

# Installation

1. Create a file secrets/.db_password that includes a password used for accessing the Postgresql instance