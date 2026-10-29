import sqlite3


CURRENT_SCHEMA_VERSION = 51


def initialize_schema(connection: sqlite3.Connection) -> None:
    with connection:
        version = connection.execute("PRAGMA user_version").fetchone()[0]

        # Include version-only barriers in the same rollback boundary as DDL.
        if version < CURRENT_SCHEMA_VERSION and not connection.in_transaction:
            connection.execute("BEGIN")

        if version == 0:
            _initialize_version_1(connection)
            version = 1
        if version == 1:
            _migrate_version_1_to_2(connection)
            version = 2
        if version == 2:
            _migrate_version_2_to_3(connection)
            version = 3
        if version == 3:
            _migrate_version_3_to_4(connection)
            version = 4
        if version == 4:
            _migrate_version_4_to_5(connection)
            version = 5
        if version == 5:
            _migrate_version_5_to_6(connection)
            version = 6
        if version == 6:
            _migrate_version_6_to_7(connection)
            version = 7
        if version == 7:
            _migrate_version_7_to_8(connection)
            version = 8
        if version == 8:
            _migrate_version_8_to_9(connection)
            version = 9
        if version == 9:
            _migrate_version_9_to_10(connection)
            version = 10
        if version == 10:
            _migrate_version_10_to_11(connection)
            version = 11
        if version == 11:
            _migrate_version_11_to_12(connection)
            version = 12
        if version == 12:
            _migrate_version_12_to_13(connection)
            version = 13
        if version == 13:
            _migrate_version_13_to_14(connection)
            version = 14
        if version == 14:
            _migrate_version_14_to_15(connection)
            version = 15
        if version == 15:
            _migrate_version_15_to_16(connection)
            version = 16
        if version == 16:
            _migrate_version_16_to_17(connection)
            version = 17
        if version == 17:
            _migrate_version_17_to_18(connection)
            version = 18
        if version == 18:
            _migrate_version_18_to_19(connection)
            version = 19
        if version == 19:
            _migrate_version_19_to_20(connection)
            version = 20
        if version == 20:
            _migrate_version_20_to_21(connection)
            version = 21
        if version == 21:
            _migrate_version_21_to_22(connection)
            version = 22
        if version == 22:
            _migrate_version_22_to_23(connection)
            version = 23
        if version == 23:
            _migrate_version_23_to_24(connection)
            version = 24
        if version == 24:
            _migrate_version_24_to_25(connection)
            version = 25
        if version == 25:
            _migrate_version_25_to_26(connection)
            version = 26
        if version == 26:
            _migrate_version_26_to_27(connection)
            version = 27
        if version == 27:
            _migrate_version_27_to_28(connection)
            version = 28
        if version == 28:
            _migrate_version_28_to_29(connection)
            version = 29
        if version == 29:
            _migrate_version_29_to_30(connection)
            version = 30
        if version == 30:
            _migrate_version_30_to_31(connection)
            version = 31
        if version == 31:
            _migrate_version_31_to_32(connection)
            version = 32
        if version == 32:
            _migrate_version_32_to_33(connection)
            version = 33
        if version == 33:
            _migrate_version_33_to_34(connection)
            version = 34
        if version == 34:
            _migrate_version_34_to_35(connection)
            version = 35
        if version == 35:
            _migrate_version_35_to_36(connection)
            version = 36
        if version == 36:
            _migrate_version_36_to_37(connection)
            version = 37
        if version == 37:
            _migrate_version_37_to_38(connection)
            version = 38
        if version == 38:
            _migrate_version_38_to_39(connection)
            version = 39
        if version == 39:
            _migrate_version_39_to_40(connection)
            version = 40
        if version == 40:
            _migrate_version_40_to_41(connection)
            version = 41
        if version == 41:
            _migrate_version_41_to_42(connection)
            version = 42
        if version == 42:
            _migrate_version_42_to_43(connection)
            version = 43
        if version == 43:
            _migrate_version_43_to_44(connection)
            version = 44
        if version == 44:
            _migrate_version_44_to_45(connection)
            version = 45
        if version == 45:
            # Versioned bounded Review proofs live inside immutable assessment receipts.
            # Older readers must not open a database that may contain envelope v2.
            connection.execute("PRAGMA user_version = 46")
            version = 46

        if version == 46:
            _migrate_version_46_to_47(connection)
            version = 47

        if version == 47:
            _migrate_version_47_to_48(connection)
            version = 48

        if version == 48:
            _migrate_version_48_to_49(connection)
            version = 49

        if version == 49:
            _migrate_version_49_to_50(connection)
            version = 50

        if version == 50:
            _migrate_version_50_to_51(connection)
            version = 51

        if version != CURRENT_SCHEMA_VERSION:
            raise RuntimeError(f"Unsupported database schema version: {version}")


def _initialize_version_1(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS tda_analysis (
            id TEXT PRIMARY KEY,
            analysis_date TEXT NOT NULL,
            instrument TEXT NOT NULL,
            weekly_bias TEXT NOT NULL,
            daily_bias TEXT NOT NULL,
            primary_draw TEXT NOT NULL,
            secondary_draw TEXT NOT NULL DEFAULT '',
            narrative TEXT NOT NULL DEFAULT ''
        )
        """
    )
    connection.execute("PRAGMA user_version = 1")


def _migrate_version_1_to_2(connection: sqlite3.Connection) -> None:
    columns = connection.execute("PRAGMA table_info(tda_analysis)").fetchall()
    column_names = {column[1] for column in columns}
    if "status" not in column_names:
        connection.execute("ALTER TABLE tda_analysis ADD COLUMN status TEXT NOT NULL DEFAULT 'Draft'")
    connection.execute("PRAGMA user_version = 2")


def _migrate_version_2_to_3(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE tda_analysis_v3 (
            id TEXT PRIMARY KEY,
            analysis_date TEXT NOT NULL,
            instrument TEXT NOT NULL,
            weekly_bias TEXT,
            daily_bias TEXT,
            primary_draw TEXT,
            secondary_draw TEXT NOT NULL DEFAULT '',
            narrative TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'Draft'
        )
        """
    )
    connection.execute(
        """
        INSERT INTO tda_analysis_v3 (
            id, analysis_date, instrument, weekly_bias, daily_bias,
            primary_draw, secondary_draw, narrative, status
        )
        SELECT id, analysis_date, instrument, weekly_bias, daily_bias,
               primary_draw, secondary_draw, narrative, status
        FROM tda_analysis
        """
    )
    connection.execute("DROP TABLE tda_analysis")
    connection.execute("ALTER TABLE tda_analysis_v3 RENAME TO tda_analysis")
    connection.execute("PRAGMA user_version = 3")


def _migrate_version_3_to_4(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE study_find (
            id TEXT PRIMARY KEY,
            observation_date TEXT NOT NULL,
            instrument TEXT NOT NULL,
            session TEXT NOT NULL,
            pattern_name TEXT NOT NULL,
            observation TEXT NOT NULL,
            available_move_handles REAL,
            notes TEXT NOT NULL DEFAULT '',
            image_path TEXT NOT NULL DEFAULT ''
        )
        """
    )
    connection.execute("PRAGMA user_version = 4")


def _migrate_version_4_to_5(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE study_find_image (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            study_find_id TEXT NOT NULL,
            image_path TEXT NOT NULL,
            image_order INTEGER NOT NULL,
            FOREIGN KEY (study_find_id) REFERENCES study_find(id) ON DELETE CASCADE
        )
        """
    )
    connection.execute("CREATE INDEX idx_study_find_image_study_find_id ON study_find_image(study_find_id)")
    connection.execute("PRAGMA user_version = 5")


def _migrate_version_5_to_6(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE study_find_draft (
            id TEXT PRIMARY KEY,
            observation_date TEXT NOT NULL,
            instrument TEXT NOT NULL DEFAULT '',
            session TEXT NOT NULL DEFAULT '',
            pattern_name TEXT NOT NULL DEFAULT '',
            observation TEXT NOT NULL DEFAULT '',
            available_move_handles REAL,
            notes TEXT NOT NULL DEFAULT '',
            image_paths TEXT NOT NULL DEFAULT '[]',
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    connection.execute("PRAGMA user_version = 6")


def _migrate_version_6_to_7(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE feedback_entry (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            category TEXT NOT NULL,
            note TEXT NOT NULL,
            context TEXT NOT NULL DEFAULT '',
            record_id TEXT NOT NULL DEFAULT '',
            app_version TEXT NOT NULL DEFAULT ''
        )
        """
    )
    connection.execute("CREATE INDEX idx_feedback_entry_created_at ON feedback_entry(created_at)")
    connection.execute("PRAGMA user_version = 7")


def _migrate_version_7_to_8(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE trade_record (
            id TEXT PRIMARY KEY,
            instrument TEXT NOT NULL,
            trade_source TEXT NOT NULL,
            account_context TEXT NOT NULL DEFAULT '',
            trade_number INTEGER NOT NULL,
            model TEXT NOT NULL DEFAULT '',
            direction TEXT NOT NULL,
            entry_tf TEXT NOT NULL DEFAULT '',
            entry_time TEXT NOT NULL,
            close_time TEXT NOT NULL,
            entry_price REAL NOT NULL,
            close_price REAL NOT NULL,
            stop_price REAL NOT NULL,
            tick_size REAL NOT NULL,
            cycle_16y TEXT NOT NULL DEFAULT '',
            quadrennial TEXT NOT NULL DEFAULT '',
            quarter TEXT NOT NULL DEFAULT '',
            month TEXT NOT NULL DEFAULT '',
            week TEXT NOT NULL DEFAULT '',
            day TEXT NOT NULL DEFAULT '',
            session TEXT NOT NULL DEFAULT '',
            macro_90m TEXT NOT NULL DEFAULT '',
            summary TEXT NOT NULL DEFAULT ''
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE trade_record_image (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_record_id TEXT NOT NULL,
            image_path TEXT NOT NULL,
            image_order INTEGER NOT NULL,
            FOREIGN KEY (trade_record_id) REFERENCES trade_record(id) ON DELETE CASCADE
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE trade_record_draft (
            id TEXT PRIMARY KEY,
            payload TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    connection.execute("PRAGMA user_version = 8")


def _migrate_version_8_to_9(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE tda_station_session (
            id TEXT PRIMARY KEY,
            blueprint_revision TEXT NOT NULL,
            current_station_id TEXT NOT NULL,
            observations_json TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    connection.execute("CREATE INDEX idx_tda_station_session_updated_at ON tda_station_session(updated_at)")
    connection.execute("PRAGMA user_version = 9")


def _migrate_version_9_to_10(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE trading_day_session (
            id TEXT PRIMARY KEY,
            blueprint_revision TEXT NOT NULL,
            mode_ids_json TEXT NOT NULL,
            current_mode_id TEXT NOT NULL,
            completed_mode_ids_json TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    connection.execute("CREATE INDEX idx_trading_day_session_updated_at ON trading_day_session(updated_at)")
    connection.execute("PRAGMA user_version = 10")


def _migrate_version_10_to_11(connection: sqlite3.Connection) -> None:
    connection.execute("ALTER TABLE trading_day_session ADD COLUMN status TEXT NOT NULL DEFAULT 'Active'")
    connection.execute("ALTER TABLE trading_day_session ADD COLUMN day_outcome TEXT NOT NULL DEFAULT ''")
    connection.execute("ALTER TABLE trading_day_session ADD COLUMN transitions_json TEXT NOT NULL DEFAULT '[]'")
    connection.execute("PRAGMA user_version = 11")


def _migrate_version_11_to_12(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE trading_day (
            id TEXT PRIMARY KEY,
            futures_day_label TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'Active',
            active_session_run_id TEXT NOT NULL DEFAULT '',
            started_at TEXT NOT NULL,
            completed_at TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL
        )
        """
    )
    connection.execute("CREATE INDEX idx_trading_day_updated_at ON trading_day(updated_at)")
    connection.execute(
        """
        CREATE TABLE trading_session_run (
            id TEXT PRIMARY KEY,
            trading_day_id TEXT NOT NULL,
            session_name TEXT NOT NULL,
            process_session_id TEXT NOT NULL,
            tda_station_session_id TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'Active',
            outcome TEXT NOT NULL DEFAULT '',
            started_at TEXT NOT NULL,
            concluded_at TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL,
            FOREIGN KEY (trading_day_id) REFERENCES trading_day(id) ON DELETE CASCADE,
            FOREIGN KEY (process_session_id) REFERENCES trading_day_session(id) ON DELETE RESTRICT
        )
        """
    )
    connection.execute("CREATE INDEX idx_trading_session_run_day ON trading_session_run(trading_day_id, started_at)")
    connection.execute("PRAGMA user_version = 12")


def _migrate_version_12_to_13(connection: sqlite3.Connection) -> None:
    connection.execute("ALTER TABLE trading_session_run ADD COLUMN current_thesis_state TEXT NOT NULL DEFAULT 'Not Set'")
    connection.execute("ALTER TABLE trading_session_run ADD COLUMN evidence_json TEXT NOT NULL DEFAULT '[]'")
    connection.execute("PRAGMA user_version = 13")


def _migrate_version_13_to_14(connection: sqlite3.Connection) -> None:
    connection.execute("ALTER TABLE trading_session_run ADD COLUMN review_process_adherence TEXT NOT NULL DEFAULT 'Not Reviewed'")
    connection.execute("ALTER TABLE trading_session_run ADD COLUMN review_takeaway TEXT NOT NULL DEFAULT ''")
    connection.execute("ALTER TABLE trading_session_run ADD COLUMN review_film_night INTEGER NOT NULL DEFAULT 0")
    connection.execute("PRAGMA user_version = 14")


def _migrate_version_14_to_15(connection: sqlite3.Connection) -> None:
    connection.execute("ALTER TABLE trading_session_run ADD COLUMN entry_condition_states_json TEXT NOT NULL DEFAULT '{}'")
    connection.execute("PRAGMA user_version = 15")


def _migrate_version_15_to_16(connection: sqlite3.Connection) -> None:
    connection.execute("ALTER TABLE tda_station_session ADD COLUMN watch_points_json TEXT NOT NULL DEFAULT '[]'")
    connection.execute("ALTER TABLE trading_session_run ADD COLUMN watch_point_states_json TEXT NOT NULL DEFAULT '{}'")
    connection.execute("PRAGMA user_version = 16")


def _migrate_version_16_to_17(connection: sqlite3.Connection) -> None:
    connection.execute("ALTER TABLE trading_session_run ADD COLUMN run_environment TEXT NOT NULL DEFAULT 'Live'")
    connection.execute("ALTER TABLE trading_session_run ADD COLUMN trade_plan_revision TEXT NOT NULL DEFAULT ''")
    connection.execute("PRAGMA user_version = 17")


def _migrate_version_17_to_18(connection: sqlite3.Connection) -> None:
    connection.execute("ALTER TABLE trading_session_run ADD COLUMN review_interpretation_outcome TEXT NOT NULL DEFAULT 'Not Reviewed'")
    connection.execute("PRAGMA user_version = 18")


def _migrate_version_18_to_19(connection: sqlite3.Connection) -> None:
    connection.execute("ALTER TABLE trading_session_run ADD COLUMN selected_playbook_id TEXT NOT NULL DEFAULT ''")
    connection.execute("ALTER TABLE trading_session_run ADD COLUMN selected_playbook_revision TEXT NOT NULL DEFAULT ''")
    connection.execute("ALTER TABLE trading_session_run ADD COLUMN playbook_snapshot_json TEXT NOT NULL DEFAULT '{}'")
    connection.execute("PRAGMA user_version = 19")


def _migrate_version_19_to_20(connection: sqlite3.Connection) -> None:
    connection.execute("ALTER TABLE trading_session_run ADD COLUMN setup_candidates_json TEXT NOT NULL DEFAULT '[]'")
    connection.execute("PRAGMA user_version = 20")


def _migrate_version_20_to_21(connection: sqlite3.Connection) -> None:
    connection.execute("ALTER TABLE trading_session_run ADD COLUMN authorization_policy_snapshot_json TEXT NOT NULL DEFAULT '[]'")
    connection.execute("ALTER TABLE trading_session_run ADD COLUMN authorization_gate_states_json TEXT NOT NULL DEFAULT '{}'")
    connection.execute("PRAGMA user_version = 21")


def _migrate_version_21_to_22(connection: sqlite3.Connection) -> None:
    connection.execute(
        "ALTER TABLE trading_session_run ADD COLUMN market_time_context_json TEXT NOT NULL DEFAULT '{}'"
    )
    connection.execute("PRAGMA user_version = 22")


def _migrate_version_22_to_23(connection: sqlite3.Connection) -> None:
    connection.execute(
        "ALTER TABLE trading_session_run ADD COLUMN qt_context_json TEXT NOT NULL DEFAULT '{}'"
    )
    connection.execute("PRAGMA user_version = 23")



def _migrate_version_23_to_24(connection: sqlite3.Connection) -> None:
    connection.execute(
        "ALTER TABLE trading_session_run ADD COLUMN study_context_json TEXT NOT NULL DEFAULT '{}'"
    )
    connection.execute("PRAGMA user_version = 24")



def _migrate_version_24_to_25(connection: sqlite3.Connection) -> None:
    connection.execute(
        "ALTER TABLE trading_session_run ADD COLUMN run_purpose TEXT NOT NULL DEFAULT ''"
    )
    connection.execute("PRAGMA user_version = 25")



def _migrate_version_25_to_26(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE competency_assessment (
            trade_plan_id TEXT NOT NULL,
            trade_plan_revision TEXT NOT NULL,
            competency_id TEXT NOT NULL,
            state TEXT NOT NULL DEFAULT 'Not Assessed',
            note TEXT NOT NULL DEFAULT '',
            source TEXT NOT NULL DEFAULT 'Manual',
            updated_at TEXT NOT NULL,
            PRIMARY KEY (trade_plan_id, competency_id)
        )
        """
    )
    connection.execute(
        "CREATE INDEX idx_competency_assessment_plan "
        "ON competency_assessment(trade_plan_id, competency_id)"
    )
    connection.execute("PRAGMA user_version = 26")


def _migrate_version_26_to_27(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE summary_template (
            template_id TEXT NOT NULL,
            revision INTEGER NOT NULL,
            kind TEXT NOT NULL,
            name TEXT NOT NULL,
            body TEXT NOT NULL,
            created_at TEXT NOT NULL,
            PRIMARY KEY (template_id, revision)
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE summary_template_active (
            kind TEXT PRIMARY KEY,
            template_id TEXT NOT NULL,
            revision INTEGER NOT NULL,
            FOREIGN KEY (template_id, revision)
                REFERENCES summary_template(template_id, revision)
                ON DELETE RESTRICT
        )
        """
    )
    connection.execute(
        "CREATE INDEX idx_summary_template_kind "
        "ON summary_template(kind, template_id, revision)"
    )
    connection.execute("PRAGMA user_version = 27")

def _migrate_version_27_to_28(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE competency_evidence (
            id TEXT PRIMARY KEY,
            trade_plan_id TEXT NOT NULL,
            trade_plan_revision TEXT NOT NULL,
            competency_id TEXT NOT NULL,
            competency_name TEXT NOT NULL,
            competency_category TEXT NOT NULL DEFAULT '',
            trading_run_id TEXT NOT NULL,
            run_environment TEXT NOT NULL,
            run_purpose TEXT NOT NULL,
            study_outcome TEXT NOT NULL,
            note TEXT NOT NULL DEFAULT '',
            study_question TEXT NOT NULL DEFAULT '',
            study_hypothesis TEXT NOT NULL DEFAULT '',
            study_scope TEXT NOT NULL DEFAULT '',
            market_time_context_json TEXT NOT NULL DEFAULT '{}',
            qt_context_json TEXT NOT NULL DEFAULT '{}',
            source TEXT NOT NULL DEFAULT 'Study Review',
            recorded_at TEXT NOT NULL,
            UNIQUE (trading_run_id, competency_id)
        )
        """
    )
    connection.execute(
        "CREATE INDEX idx_competency_evidence_competency "
        "ON competency_evidence(trade_plan_id, competency_id, recorded_at)"
    )
    connection.execute(
        "CREATE INDEX idx_competency_evidence_run "
        "ON competency_evidence(trading_run_id)"
    )
    connection.execute("PRAGMA user_version = 28")



def _migrate_version_28_to_29(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE competency_development_direction (
            trade_plan_id TEXT NOT NULL,
            trade_plan_revision TEXT NOT NULL,
            competency_id TEXT NOT NULL,
            direction TEXT NOT NULL,
            note TEXT NOT NULL DEFAULT '',
            supporting_evidence_ids_json TEXT NOT NULL DEFAULT '[]',
            source TEXT NOT NULL DEFAULT 'Review / Development',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (trade_plan_id, competency_id)
        )
        """
    )
    connection.execute(
        "CREATE INDEX idx_competency_development_direction_plan "
        "ON competency_development_direction(trade_plan_id, competency_id)"
    )
    connection.execute("PRAGMA user_version = 29")



def _migrate_version_29_to_30(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE competency_cross_run_observation (
            trade_plan_id TEXT NOT NULL,
            trade_plan_revision TEXT NOT NULL,
            competency_id TEXT NOT NULL,
            observation TEXT NOT NULL DEFAULT '',
            supporting_evidence_ids_json TEXT NOT NULL DEFAULT '[]',
            source TEXT NOT NULL DEFAULT 'Review / Development',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (trade_plan_id, competency_id)
        )
        """
    )
    connection.execute(
        "CREATE INDEX idx_competency_cross_run_observation_plan_competency "
        "ON competency_cross_run_observation(trade_plan_id, competency_id)"
    )
    connection.execute("PRAGMA user_version = 30")



def _migrate_version_30_to_31(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE competency_evidence_maturity (
            trade_plan_id TEXT NOT NULL,
            trade_plan_revision TEXT NOT NULL,
            competency_id TEXT NOT NULL,
            progression_boundary TEXT NOT NULL,
            maturity_state TEXT NOT NULL DEFAULT 'Not Assessed',
            maturity_note TEXT NOT NULL DEFAULT '',
            consistency_note TEXT NOT NULL DEFAULT '',
            known_gap_note TEXT NOT NULL DEFAULT '',
            source TEXT NOT NULL DEFAULT 'Review / Development',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (
                trade_plan_id,
                competency_id,
                progression_boundary
            )
        )
        """
    )
    connection.execute(
        "CREATE INDEX idx_competency_evidence_maturity_plan_competency "
        "ON competency_evidence_maturity(trade_plan_id, competency_id)"
    )
    connection.execute("PRAGMA user_version = 31")



def _migrate_version_31_to_32(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE progression_certification (
            trade_plan_id TEXT NOT NULL,
            trade_plan_revision TEXT NOT NULL,
            progression_boundary TEXT NOT NULL,
            requirement_id TEXT NOT NULL,
            confirmed INTEGER NOT NULL DEFAULT 0,
            note TEXT NOT NULL DEFAULT '',
            confirmed_at TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL,
            PRIMARY KEY (
                trade_plan_id,
                trade_plan_revision,
                progression_boundary,
                requirement_id
            )
        )
        """
    )
    connection.execute(
        "CREATE INDEX idx_progression_certification_plan_boundary "
        "ON progression_certification("
        "trade_plan_id, trade_plan_revision, progression_boundary"
        ")"
    )
    connection.execute("PRAGMA user_version = 32")



def _migrate_version_32_to_33(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE progression_attainment (
            id TEXT PRIMARY KEY,
            trade_plan_id TEXT NOT NULL,
            trade_plan_revision TEXT NOT NULL,
            progression_boundary TEXT NOT NULL,
            policy_id TEXT NOT NULL,
            eligibility_snapshot_json TEXT NOT NULL,
            attained_environment TEXT NOT NULL,
            attained_at TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT 'Process Run Launcher',
            note TEXT NOT NULL DEFAULT '',
            UNIQUE (
                trade_plan_id,
                trade_plan_revision,
                progression_boundary,
                policy_id
            )
        )
        """
    )
    connection.execute(
        "CREATE INDEX idx_progression_attainment_plan_boundary "
        "ON progression_attainment("
        "trade_plan_id, progression_boundary, attained_at"
        ")"
    )
    connection.execute(
        """
        CREATE TABLE progression_regression_review (
            trade_plan_id TEXT NOT NULL,
            trade_plan_revision TEXT NOT NULL,
            progression_boundary TEXT NOT NULL,
            prior_attainment_id TEXT NOT NULL,
            eligibility_snapshot_json TEXT NOT NULL,
            classification TEXT NOT NULL,
            note TEXT NOT NULL DEFAULT '',
            supporting_evidence_ids_json TEXT NOT NULL DEFAULT '[]',
            source TEXT NOT NULL DEFAULT 'Review / Development',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (
                trade_plan_id,
                trade_plan_revision,
                progression_boundary,
                prior_attainment_id
            ),
            FOREIGN KEY (prior_attainment_id)
                REFERENCES progression_attainment(id)
                ON DELETE RESTRICT
        )
        """
    )
    connection.execute(
        "CREATE INDEX idx_progression_regression_review_plan_boundary "
        "ON progression_regression_review("
        "trade_plan_id, trade_plan_revision, progression_boundary"
        ")"
    )
    connection.execute("PRAGMA user_version = 33")



def _migrate_version_33_to_34(connection: sqlite3.Connection) -> None:
    connection.execute(
        "ALTER TABLE trading_session_run "
        "ADD COLUMN review_observed_qt_context_json "
        "TEXT NOT NULL DEFAULT '{}'"
    )
    connection.execute(
        "ALTER TABLE trading_session_run "
        "ADD COLUMN review_qt_context_note "
        "TEXT NOT NULL DEFAULT ''"
    )
    connection.execute("PRAGMA user_version = 34")



def _migrate_version_34_to_35(connection: sqlite3.Connection) -> None:
    connection.execute(
        "ALTER TABLE trading_session_run "
        "ADD COLUMN market_context_snapshot_json "
        "TEXT NOT NULL DEFAULT '{}'"
    )
    connection.execute("PRAGMA user_version = 35")


def _migrate_version_35_to_36(connection: sqlite3.Connection) -> None:
    connection.execute(
        "ALTER TABLE trading_session_run "
        "ADD COLUMN context_rule_snapshot_json TEXT NOT NULL DEFAULT '[]'"
    )
    connection.execute("PRAGMA user_version = 36")


def _migrate_version_36_to_37(connection: sqlite3.Connection) -> None:
    # Existing snapshot JSON is preserved. Missing coverage/precision is read
    # as unknown rather than fabricating a provider claim during migration.
    connection.execute("""
        CREATE TABLE context_source_capture (
            id TEXT PRIMARY KEY,
            imported_at TEXT NOT NULL,
            payload_json TEXT NOT NULL
        )
    """)
    connection.execute("""
        CREATE TRIGGER context_capture_no_update BEFORE UPDATE ON context_source_capture
        BEGIN SELECT RAISE(ABORT, 'Source captures are immutable'); END
    """)
    connection.execute("""
        CREATE TRIGGER context_capture_no_delete BEFORE DELETE ON context_source_capture
        BEGIN SELECT RAISE(ABORT, 'Source captures are immutable'); END
    """)
    connection.execute("PRAGMA user_version = 37")


def _migrate_version_37_to_38(connection: sqlite3.Connection) -> None:
    # SQLite DDL alone does not open a Python-managed transaction. Keep every
    # additive table/trigger and the version bump atomic on existing v37 files.
    if not connection.in_transaction:
        connection.execute("BEGIN")
    connection.execute("""
        CREATE TABLE amdx_cycle_identity (
            id TEXT NOT NULL PRIMARY KEY,
            payload_json TEXT NOT NULL
        )
    """)
    connection.execute("""
        CREATE TABLE amdx_definition_revision (
            plan_revision TEXT NOT NULL,
            rule_id TEXT NOT NULL,
            rule_revision TEXT NOT NULL,
            publication TEXT NOT NULL CHECK(publication IN ('Candidate', 'Published')),
            payload_json TEXT NOT NULL,
            PRIMARY KEY (plan_revision, rule_id, rule_revision, publication)
        )
    """)
    connection.execute("""
        CREATE TABLE amdx_claim (
            sequence INTEGER PRIMARY KEY CHECK(sequence > 0),
            id TEXT NOT NULL UNIQUE,
            run_id TEXT NOT NULL REFERENCES trading_session_run(id) ON DELETE RESTRICT,
            branch_id TEXT NOT NULL,
            channel TEXT NOT NULL CHECK(channel IN ('Expected', 'Observed')),
            cycle_id TEXT NOT NULL REFERENCES amdx_cycle_identity(id) ON DELETE RESTRICT,
            parent_claim_id TEXT,
            payload_json TEXT NOT NULL,
            UNIQUE(id, run_id),
            FOREIGN KEY (parent_claim_id, run_id) REFERENCES amdx_claim(id, run_id) ON DELETE RESTRICT
        )
    """)
    connection.execute("CREATE INDEX idx_amdx_claim_run ON amdx_claim(run_id, sequence)")
    connection.execute("""
        CREATE TABLE amdx_evaluation (
            sequence INTEGER PRIMARY KEY CHECK(sequence > 0),
            id TEXT NOT NULL UNIQUE,
            run_id TEXT NOT NULL REFERENCES trading_session_run(id) ON DELETE RESTRICT,
            cycle_id TEXT NOT NULL REFERENCES amdx_cycle_identity(id) ON DELETE RESTRICT,
            recorded_at TEXT NOT NULL,
            basis_claim_id TEXT,
            payload_json TEXT NOT NULL,
            FOREIGN KEY (basis_claim_id, run_id) REFERENCES amdx_claim(id, run_id) ON DELETE RESTRICT
        )
    """)
    connection.execute("CREATE INDEX idx_amdx_evaluation_run ON amdx_evaluation(run_id, sequence)")
    for table in ("amdx_cycle_identity", "amdx_definition_revision", "amdx_claim", "amdx_evaluation"):
        for operation in ("UPDATE", "DELETE"):
            connection.execute(f"""
                CREATE TRIGGER {table}_no_{operation.lower()}
                BEFORE {operation} ON {table}
                BEGIN SELECT RAISE(ABORT, 'AMDX history is immutable'); END
            """)
        # REPLACE can bypass DELETE triggers when recursive_triggers is off.
        # Guard conflicting inserts explicitly, including sequence collisions.
        if table == "amdx_definition_revision":
            conflict = "plan_revision = NEW.plan_revision AND rule_id = NEW.rule_id AND rule_revision = NEW.rule_revision AND publication = NEW.publication"
        elif table in ("amdx_claim", "amdx_evaluation"):
            conflict = "id = NEW.id OR sequence = NEW.sequence"
        else:
            conflict = "id = NEW.id"
        connection.execute(f"""
            CREATE TRIGGER {table}_no_replace BEFORE INSERT ON {table}
            WHEN EXISTS (SELECT 1 FROM {table} WHERE {conflict})
            BEGIN SELECT RAISE(ABORT, 'AMDX history is immutable'); END
        """)
    connection.execute("PRAGMA user_version = 38")


def _migrate_version_38_to_39(connection: sqlite3.Connection) -> None:
    # New replay policy requires a forward guard even though claim rows retain
    # the existing table shape. Receipts reserve identities for semantic no-ops.
    if not connection.in_transaction:
        connection.execute("BEGIN")
    connection.execute("""
        CREATE TABLE amdx_working_command (
            id TEXT NOT NULL PRIMARY KEY,
            run_id TEXT NOT NULL REFERENCES trading_session_run(id) ON DELETE RESTRICT,
            cycle_id TEXT NOT NULL REFERENCES amdx_cycle_identity(id) ON DELETE RESTRICT,
            parent_claim_id TEXT,
            result_claim_id TEXT,
            changed INTEGER NOT NULL CHECK(changed IN (0, 1)),
            payload_json TEXT NOT NULL,
            FOREIGN KEY (parent_claim_id, run_id) REFERENCES amdx_claim(id, run_id) ON DELETE RESTRICT,
            FOREIGN KEY (result_claim_id, run_id) REFERENCES amdx_claim(id, run_id) ON DELETE RESTRICT
        )
    """)
    for operation in ("UPDATE", "DELETE"):
        connection.execute(f"""
            CREATE TRIGGER amdx_working_command_no_{operation.lower()}
            BEFORE {operation} ON amdx_working_command
            BEGIN SELECT RAISE(ABORT, 'AMDX history is immutable'); END
        """)
    connection.execute("""
        CREATE TRIGGER amdx_working_command_no_replace BEFORE INSERT ON amdx_working_command
        WHEN EXISTS (SELECT 1 FROM amdx_working_command WHERE id = NEW.id)
        BEGIN SELECT RAISE(ABORT, 'AMDX history is immutable'); END
    """)
    connection.execute("PRAGMA user_version = 39")


def _migrate_version_39_to_40(connection: sqlite3.Connection) -> None:
    if not connection.in_transaction:
        connection.execute("BEGIN")
    connection.execute("""
        CREATE TABLE amdx_comparison (
            sequence INTEGER PRIMARY KEY CHECK(sequence > 0),
            id TEXT NOT NULL UNIQUE,
            run_id TEXT NOT NULL REFERENCES trading_session_run(id) ON DELETE RESTRICT,
            branch_id TEXT NOT NULL,
            cycle_id TEXT NOT NULL REFERENCES amdx_cycle_identity(id) ON DELETE RESTRICT,
            expected_claim_id TEXT,
            observed_claim_id TEXT NOT NULL,
            parent_comparison_id TEXT,
            payload_json TEXT NOT NULL,
            UNIQUE(id, run_id),
            FOREIGN KEY (expected_claim_id, run_id) REFERENCES amdx_claim(id, run_id) ON DELETE RESTRICT,
            FOREIGN KEY (observed_claim_id, run_id) REFERENCES amdx_claim(id, run_id) ON DELETE RESTRICT,
            FOREIGN KEY (parent_comparison_id, run_id) REFERENCES amdx_comparison(id, run_id) ON DELETE RESTRICT
        )
    """)
    connection.execute("CREATE INDEX idx_amdx_comparison_run ON amdx_comparison(run_id, sequence)")
    connection.execute("""
        CREATE TABLE amdx_review_command (
            id TEXT NOT NULL PRIMARY KEY,
            run_id TEXT NOT NULL,
            operation TEXT NOT NULL CHECK(operation IN ('Pair', 'ObserveAndPair')),
            observed_claim_id TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            FOREIGN KEY (id, run_id) REFERENCES amdx_comparison(id, run_id) ON DELETE RESTRICT,
            FOREIGN KEY (observed_claim_id, run_id) REFERENCES amdx_claim(id, run_id) ON DELETE RESTRICT
        )
    """)
    connection.execute("""CREATE UNIQUE INDEX idx_amdx_review_observed_producer
                       ON amdx_review_command(observed_claim_id) WHERE operation = 'ObserveAndPair'""")
    for table in ("amdx_comparison", "amdx_review_command"):
        for operation in ("UPDATE", "DELETE"):
            connection.execute(f"""
                CREATE TRIGGER {table}_no_{operation.lower()}
                BEFORE {operation} ON {table}
                BEGIN SELECT RAISE(ABORT, 'AMDX Review history is immutable'); END
            """)
        conflict = "id = NEW.id OR sequence = NEW.sequence" if table == "amdx_comparison" else "id = NEW.id"
        connection.execute(f"""
            CREATE TRIGGER {table}_no_replace BEFORE INSERT ON {table}
            WHEN EXISTS (SELECT 1 FROM {table} WHERE {conflict})
            BEGIN SELECT RAISE(ABORT, 'AMDX Review history is immutable'); END
        """)
    connection.execute("PRAGMA user_version = 40")


def _migrate_version_40_to_41(connection: sqlite3.Connection) -> None:
    if not connection.in_transaction:
        connection.execute("BEGIN")
    connection.execute("""
        CREATE TABLE amdx_observed_command (
            id TEXT NOT NULL PRIMARY KEY,
            comparison_id TEXT NOT NULL UNIQUE,
            run_id TEXT NOT NULL REFERENCES trading_session_run(id) ON DELETE RESTRICT,
            cycle_id TEXT NOT NULL REFERENCES amdx_cycle_identity(id) ON DELETE RESTRICT,
            parent_claim_id TEXT,
            parent_comparison_id TEXT,
            result_claim_id TEXT,
            result_comparison_id TEXT,
            changed INTEGER NOT NULL CHECK(changed IN (0, 1)),
            basis_count INTEGER NOT NULL CHECK(basis_count >= 0),
            comparison_count INTEGER NOT NULL CHECK(comparison_count >= 0),
            payload_json TEXT NOT NULL,
            FOREIGN KEY (parent_claim_id, run_id) REFERENCES amdx_claim(id, run_id) ON DELETE RESTRICT,
            FOREIGN KEY (result_claim_id, run_id) REFERENCES amdx_claim(id, run_id) ON DELETE RESTRICT,
            FOREIGN KEY (parent_comparison_id, run_id) REFERENCES amdx_comparison(id, run_id) ON DELETE RESTRICT,
            FOREIGN KEY (result_comparison_id, run_id) REFERENCES amdx_comparison(id, run_id) ON DELETE RESTRICT
        )
    """)
    for operation in ("UPDATE", "DELETE"):
        connection.execute(f"""
            CREATE TRIGGER amdx_observed_command_no_{operation.lower()}
            BEFORE {operation} ON amdx_observed_command
            BEGIN SELECT RAISE(ABORT, 'Observed AMDX history is immutable'); END
        """)
    connection.execute("""
        CREATE TRIGGER amdx_observed_command_no_replace BEFORE INSERT ON amdx_observed_command
        WHEN EXISTS (SELECT 1 FROM amdx_observed_command WHERE id=NEW.id OR comparison_id=NEW.comparison_id)
        BEGIN SELECT RAISE(ABORT, 'Observed AMDX history is immutable'); END
    """)
    connection.execute("PRAGMA user_version = 41")


def _migrate_version_41_to_42(connection: sqlite3.Connection) -> None:
    if not connection.in_transaction:
        connection.execute("BEGIN")
    connection.execute("""
        CREATE TABLE amdx_catalog (
            id TEXT NOT NULL PRIMARY KEY,
            instrument TEXT NOT NULL,
            payload_json TEXT NOT NULL
        )
    """)
    connection.execute("CREATE INDEX idx_amdx_catalog_instrument ON amdx_catalog(instrument)")
    connection.execute("""
        CREATE TABLE amdx_catalog_command (
            sequence INTEGER PRIMARY KEY,
            id TEXT NOT NULL UNIQUE,
            catalog_id TEXT NOT NULL REFERENCES amdx_catalog(id) ON DELETE RESTRICT,
            cycle_id TEXT NOT NULL REFERENCES amdx_cycle_identity(id) ON DELETE RESTRICT,
            channel TEXT NOT NULL CHECK(channel IN ('Expected', 'Observed')),
            payload_json TEXT NOT NULL
        )
    """)
    connection.execute("CREATE INDEX idx_amdx_catalog_command_scope ON amdx_catalog_command(catalog_id,cycle_id,channel,sequence)")
    for table in ("amdx_catalog", "amdx_catalog_command"):
        for operation in ("UPDATE", "DELETE"):
            connection.execute(f"""
                CREATE TRIGGER {table}_no_{operation.lower()} BEFORE {operation} ON {table}
                BEGIN SELECT RAISE(ABORT, 'AMDX catalog history is immutable'); END
            """)
        conflict = "id=NEW.id" + (" OR sequence=NEW.sequence" if table.endswith("_command") else "")
        connection.execute(f"""
            CREATE TRIGGER {table}_no_replace BEFORE INSERT ON {table}
            WHEN EXISTS (SELECT 1 FROM {table} WHERE {conflict})
            BEGIN SELECT RAISE(ABORT, 'AMDX catalog history is immutable'); END
        """)
    connection.execute("PRAGMA user_version = 42")


def _migrate_version_42_to_43(connection: sqlite3.Connection) -> None:
    if not connection.in_transaction:
        connection.execute("BEGIN")
    connection.execute("CREATE UNIQUE INDEX idx_amdx_catalog_owner_instrument ON amdx_catalog(id,instrument)")
    connection.execute("""
        CREATE TABLE amdx_master_binding (
            id TEXT NOT NULL PRIMARY KEY,
            instrument TEXT NOT NULL UNIQUE,
            catalog_id TEXT NOT NULL UNIQUE,
            payload_json TEXT NOT NULL,
            FOREIGN KEY (catalog_id,instrument) REFERENCES amdx_catalog(id,instrument) ON DELETE RESTRICT
        )
    """)
    for operation in ("UPDATE", "DELETE"):
        connection.execute(f"""
            CREATE TRIGGER amdx_master_binding_no_{operation.lower()}
            BEFORE {operation} ON amdx_master_binding
            BEGIN SELECT RAISE(ABORT, 'AMDX master ownership is immutable'); END
        """)
    connection.execute("""
        CREATE TRIGGER amdx_master_binding_no_replace BEFORE INSERT ON amdx_master_binding
        WHEN EXISTS (SELECT 1 FROM amdx_master_binding
                     WHERE id=NEW.id OR instrument=NEW.instrument OR catalog_id=NEW.catalog_id)
        BEGIN SELECT RAISE(ABORT, 'AMDX master ownership is immutable'); END
    """)
    connection.execute("PRAGMA user_version = 43")


def _migrate_version_43_to_44(connection: sqlite3.Connection) -> None:
    if not connection.in_transaction:
        connection.execute("BEGIN")
    connection.execute("CREATE UNIQUE INDEX idx_amdx_master_bound_scope ON amdx_master_binding(id,instrument,catalog_id)")
    connection.execute("""
        CREATE TABLE amdx_run_binding (
            run_id TEXT NOT NULL PRIMARY KEY REFERENCES trading_session_run(id) ON DELETE RESTRICT,
            instrument TEXT NOT NULL,
            master_binding_id TEXT NOT NULL,
            catalog_id TEXT NOT NULL,
            launch_operation_id TEXT NOT NULL UNIQUE REFERENCES amdx_run_calendar_command(id)
                DEFERRABLE INITIALLY DEFERRED,
            payload_json TEXT NOT NULL,
            FOREIGN KEY (master_binding_id,instrument,catalog_id)
                REFERENCES amdx_master_binding(id,instrument,catalog_id) ON DELETE RESTRICT
        )
    """)
    connection.execute("""
        CREATE TABLE amdx_run_capture (
            sequence INTEGER PRIMARY KEY,
            id TEXT NOT NULL UNIQUE,
            run_id TEXT NOT NULL REFERENCES amdx_run_binding(run_id) ON DELETE RESTRICT,
            operation_id TEXT NOT NULL UNIQUE REFERENCES amdx_run_calendar_command(id)
                DEFERRABLE INITIALLY DEFERRED,
            payload_json TEXT NOT NULL,
            UNIQUE(id,run_id)
        )
    """)
    connection.execute("""
        CREATE TABLE amdx_run_calendar_command (
            id TEXT NOT NULL PRIMARY KEY,
            run_id TEXT NOT NULL REFERENCES amdx_run_binding(run_id) ON DELETE RESTRICT,
            operation TEXT NOT NULL CHECK(operation IN ('Launch','Capture','WorkingEdit')),
            capture_id TEXT NOT NULL UNIQUE,
            parent_capture_id TEXT,
            catalog_command_id TEXT UNIQUE REFERENCES amdx_catalog_command(id) ON DELETE RESTRICT,
            payload_json TEXT NOT NULL,
            FOREIGN KEY (capture_id,run_id) REFERENCES amdx_run_capture(id,run_id) ON DELETE RESTRICT,
            FOREIGN KEY (parent_capture_id,run_id) REFERENCES amdx_run_capture(id,run_id) ON DELETE RESTRICT
        )
    """)
    connection.execute("CREATE INDEX idx_amdx_run_capture_scope ON amdx_run_capture(run_id,sequence)")
    for table in ("amdx_run_binding", "amdx_run_capture", "amdx_run_calendar_command"):
        for operation in ("UPDATE", "DELETE"):
            connection.execute(f"""
                CREATE TRIGGER {table}_no_{operation.lower()} BEFORE {operation} ON {table}
                BEGIN SELECT RAISE(ABORT, 'AMDX run captures are immutable'); END
            """)
        conflict = ("run_id=NEW.run_id OR launch_operation_id=NEW.launch_operation_id"
                    if table == "amdx_run_binding" else
                    "id=NEW.id OR sequence=NEW.sequence OR operation_id=NEW.operation_id"
                    if table == "amdx_run_capture" else "id=NEW.id OR capture_id=NEW.capture_id")
        connection.execute(f"""
            CREATE TRIGGER {table}_no_replace BEFORE INSERT ON {table}
            WHEN EXISTS (SELECT 1 FROM {table} WHERE {conflict})
            BEGIN SELECT RAISE(ABORT, 'AMDX run captures are immutable'); END
        """)
    connection.execute("PRAGMA user_version = 44")


def _migrate_version_44_to_45(connection: sqlite3.Connection) -> None:
    if not connection.in_transaction:
        connection.execute("BEGIN")
    connection.execute("CREATE UNIQUE INDEX idx_amdx_run_observed_binding ON amdx_run_binding(run_id,catalog_id)")
    connection.execute("CREATE UNIQUE INDEX idx_amdx_run_observed_catalog ON amdx_catalog_command(id,catalog_id)")
    connection.execute("""
        CREATE TABLE amdx_run_observed_command (
            sequence INTEGER PRIMARY KEY,
            id TEXT NOT NULL UNIQUE,
            run_id TEXT NOT NULL,
            catalog_id TEXT NOT NULL,
            catalog_command_id TEXT NOT NULL UNIQUE CHECK(catalog_command_id=id),
            parent_id TEXT,
            payload_json TEXT NOT NULL,
            UNIQUE(id,run_id),
            FOREIGN KEY (run_id,catalog_id) REFERENCES amdx_run_binding(run_id,catalog_id) ON DELETE RESTRICT,
            FOREIGN KEY (catalog_command_id,catalog_id) REFERENCES amdx_catalog_command(id,catalog_id) ON DELETE RESTRICT,
            FOREIGN KEY (parent_id,run_id) REFERENCES amdx_run_observed_command(id,run_id) ON DELETE RESTRICT
        )
    """)
    connection.execute("CREATE INDEX idx_amdx_run_observed_scope ON amdx_run_observed_command(run_id,sequence)")
    for operation in ("UPDATE", "DELETE"):
        connection.execute(f"""CREATE TRIGGER amdx_run_observed_no_{operation.lower()}
            BEFORE {operation} ON amdx_run_observed_command
            BEGIN SELECT RAISE(ABORT, 'AMDX run assessments are immutable'); END""")
    connection.execute("""CREATE TRIGGER amdx_run_observed_no_replace
        BEFORE INSERT ON amdx_run_observed_command
        WHEN EXISTS (SELECT 1 FROM amdx_run_observed_command WHERE id=NEW.id OR sequence=NEW.sequence)
        BEGIN SELECT RAISE(ABORT, 'AMDX run assessments are immutable'); END""")
    connection.execute("PRAGMA user_version = 45")


def _migrate_version_46_to_47(connection):
    if not connection.in_transaction:
        connection.execute("BEGIN")
    connection.execute("""CREATE TABLE study_investigation_capture (
        capture_id TEXT PRIMARY KEY NOT NULL,
        task_id TEXT NOT NULL,
        plan_id TEXT NOT NULL,
        plan_revision TEXT NOT NULL,
        question TEXT NOT NULL CHECK(length(trim(question)) > 0),
        instrument TEXT NOT NULL,
        market_reference TEXT NOT NULL,
        interpretation TEXT NOT NULL CHECK(interpretation IN ('Expected','Observed')),
        recorded_at TEXT NOT NULL
    )""")
    connection.execute("CREATE INDEX idx_study_investigation_task ON study_investigation_capture(task_id)")
    for operation in ("UPDATE", "DELETE"):
        connection.execute(f"""CREATE TRIGGER study_investigation_no_{operation.lower()}
            BEFORE {operation} ON study_investigation_capture
            BEGIN SELECT RAISE(ABORT, 'Study investigation associations are immutable'); END""")
    connection.execute("""CREATE TRIGGER study_investigation_no_replace
        BEFORE INSERT ON study_investigation_capture
        WHEN EXISTS(SELECT 1 FROM study_investigation_capture WHERE capture_id=NEW.capture_id)
        BEGIN SELECT RAISE(ABORT, 'Study investigation associations are immutable'); END""")
    connection.execute("PRAGMA user_version = 47")


def _migrate_version_47_to_48(connection):
    connection.execute("""CREATE TABLE study_criterion_evaluation (
        id TEXT PRIMARY KEY NOT NULL,
        task_id TEXT NOT NULL,
        payload_json TEXT NOT NULL
    )""")
    connection.execute("CREATE INDEX idx_study_criterion_task ON study_criterion_evaluation(task_id)")
    for operation in ("UPDATE", "DELETE"):
        connection.execute(f"""CREATE TRIGGER study_criterion_no_{operation.lower()}
            BEFORE {operation} ON study_criterion_evaluation
            BEGIN SELECT RAISE(ABORT, 'Study criterion evaluations are immutable'); END""")
    connection.execute("""CREATE TRIGGER study_criterion_no_replace
        BEFORE INSERT ON study_criterion_evaluation
        WHEN EXISTS(SELECT 1 FROM study_criterion_evaluation WHERE id=NEW.id)
        BEGIN SELECT RAISE(ABORT, 'Study criterion evaluations are immutable'); END""")
    connection.execute("PRAGMA user_version = 48")


def _migrate_version_48_to_49(connection):
    connection.execute("""CREATE TABLE study_question (
        id TEXT PRIMARY KEY NOT NULL,
        plan_id TEXT NOT NULL,
        payload_json TEXT NOT NULL
    )""")
    connection.execute("CREATE INDEX idx_study_question_plan ON study_question(plan_id)")
    for operation in ("UPDATE", "DELETE"):
        connection.execute(f"""CREATE TRIGGER study_question_no_{operation.lower()}
            BEFORE {operation} ON study_question
            BEGIN SELECT RAISE(ABORT, 'Study question snapshots are immutable'); END""")
    connection.execute("""CREATE TRIGGER study_question_no_replace
        BEFORE INSERT ON study_question
        WHEN EXISTS(SELECT 1 FROM study_question WHERE id=NEW.id)
        BEGIN SELECT RAISE(ABORT, 'Study question snapshots are immutable'); END""")
    connection.execute("PRAGMA user_version = 49")


def _migrate_version_49_to_50(connection):
    connection.execute("""CREATE TABLE study_finding (
        id TEXT PRIMARY KEY NOT NULL,
        plan_id TEXT NOT NULL,
        task_id TEXT,
        payload_json TEXT NOT NULL
    )""")
    connection.execute("CREATE INDEX idx_study_finding_scope ON study_finding(plan_id,task_id)")
    for operation in ("UPDATE", "DELETE"):
        connection.execute(f"""CREATE TRIGGER study_finding_no_{operation.lower()}
            BEFORE {operation} ON study_finding
            BEGIN SELECT RAISE(ABORT, 'Study finding snapshots are immutable'); END""")
    connection.execute("""CREATE TRIGGER study_finding_no_replace
        BEFORE INSERT ON study_finding
        WHEN EXISTS(SELECT 1 FROM study_finding WHERE id=NEW.id)
        BEGIN SELECT RAISE(ABORT, 'Study finding snapshots are immutable'); END""")
    connection.execute("PRAGMA user_version = 50")


def _migrate_version_50_to_51(connection):
    connection.execute("CREATE TABLE study_review (id TEXT PRIMARY KEY NOT NULL, plan_id TEXT NOT NULL, task_id TEXT NOT NULL, payload_json TEXT NOT NULL)")
    connection.execute("CREATE INDEX idx_study_review_scope ON study_review(plan_id,task_id)")
    for operation in ('UPDATE', 'DELETE'):
        connection.execute(f"CREATE TRIGGER study_review_no_{operation.lower()} BEFORE {operation} ON study_review BEGIN SELECT RAISE(ABORT, 'Study reviews are immutable'); END")
    connection.execute("CREATE TRIGGER study_review_no_replace BEFORE INSERT ON study_review WHEN EXISTS(SELECT 1 FROM study_review WHERE id=NEW.id) BEGIN SELECT RAISE(ABORT, 'Study reviews are immutable'); END")
    connection.execute("PRAGMA user_version = 51")
