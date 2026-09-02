


the architecture of logic realm of data management (ask agent to implement)

download raw data (optional to automate) in apropriate folder

preprocess data

also synthetic data generation and placement

prepare excpectable for simulation data (series e.g. solar, pv, load / powermeters)

plase prepared series in apropriate folder

---

prepare templates that will be avalible to choose in ui

---

in future this layer will interact with infrastructure layer (db)

...

17-07-2026
implement (with assistance of agent) generalized data ingestion into db and usage of it from the db (currently we experiment only on one dataset. + the experiment implies taking prepared time series)

pipeline:
laod -> parser -> prepare -> db_manager
validate -> features -> db_manager
provide in application_simulation_run
provide in ui
