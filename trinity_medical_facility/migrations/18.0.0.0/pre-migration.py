# -*- coding: utf-8 -*-

def _get_matching_columns(cr, old_table, new_table):
    """
    Get matching column names between old and new tables.
    Returns tuple: (insert_columns, select_columns)
    Columns with capital letters are quoted.
    """
    # Get all columns from both tables
    cr.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position
    """, (old_table,))
    old_columns = {row[0].lower(): row[0] for row in cr.fetchall()}

    cr.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position
    """, (new_table,))
    new_columns = {row[0].lower(): row[0] for row in cr.fetchall()}

    # Find matching columns (case-insensitive match)
    insert_cols = []
    select_cols = []

    for old_col_lower, old_col_actual in old_columns.items():
        if old_col_lower in new_columns:
            new_col_actual = new_columns[old_col_lower]
            # Quote column if it has capital letters (for INSERT)
            if new_col_actual != new_col_actual.lower():
                insert_cols.append(f'"{new_col_actual}"')
            else:
                insert_cols.append(new_col_actual)
            # Quote old column if it has capital letters (for SELECT)
            if old_col_actual != old_col_actual.lower():
                select_cols.append(f'"{old_col_actual}"')
            else:
                select_cols.append(old_col_actual)

    return insert_cols, select_cols

def migrate(cr, version):
    """
    Migration script to copy data from trinity_doctor models to trinity_medical_facility models
    """

    # 1. Copy trinity.doctor.hospital -> trinity.medical.facility
    insert_cols, select_cols = _get_matching_columns(cr, 'trinity_doctor_hospital', 'trinity_medical_facility')
    if insert_cols:
        sql = f"""
            INSERT INTO trinity_medical_facility ({', '.join(insert_cols)})
            SELECT {', '.join(select_cols)}
            FROM trinity_doctor_hospital
            WHERE id NOT IN (SELECT id FROM trinity_medical_facility);
        """
        cr.execute(sql)

    # 2. Copy trinity.doctor -> trinity.medical.facility.doctors
    insert_cols, select_cols = _get_matching_columns(cr, 'trinity_doctor', 'trinity_medical_facility_doctors')
    if insert_cols:
        sql = f"""
            INSERT INTO trinity_medical_facility_doctors ({', '.join(insert_cols)})
            SELECT {', '.join(select_cols)}
            FROM trinity_doctor
            WHERE id NOT IN (SELECT id FROM trinity_medical_facility_doctors);
        """
        cr.execute(sql)

    # 3. Copy trinity.doctor.deductions -> trinity.medical.facility.doctors.deductions
    insert_cols, select_cols = _get_matching_columns(cr, 'trinity_doctor_deductions', 'trinity_medical_facility_doctors_deductions')
    if insert_cols:
        # For deductions, we need to map doctor_id to the new doctor table
        # Replace doctor_id in select with a join
        if 'doctor_id' in [col.lower().strip('"') for col in insert_cols]:
            doctor_id_idx = next(i for i, col in enumerate(insert_cols) if col.lower().strip('"') == 'doctor_id')
            # Use a subquery to get the new doctor_id
            select_cols[doctor_id_idx] = 'tmd.id'
            sql = f"""
                INSERT INTO trinity_medical_facility_doctors_deductions ({', '.join(insert_cols)})
                SELECT {', '.join(select_cols)}
                FROM trinity_doctor_deductions td
                INNER JOIN trinity_doctor tdo ON td.doctor_id = tdo.id
                INNER JOIN trinity_medical_facility_doctors tmd ON tdo.id = tmd.id
                WHERE td.id NOT IN (SELECT id FROM trinity_medical_facility_doctors_deductions);
            """
        else:
            sql = f"""
                INSERT INTO trinity_medical_facility_doctors_deductions ({', '.join(insert_cols)})
                SELECT {', '.join(select_cols)}
                FROM trinity_doctor_deductions
                WHERE id NOT IN (SELECT id FROM trinity_medical_facility_doctors_deductions);
            """
        cr.execute(sql)

    # 4. Copy trinity.doctor.external -> trinity.medical.facility.doctors.external
    insert_cols, select_cols = _get_matching_columns(cr, 'trinity_doctor_external', 'trinity_medical_facility_doctors_external')
    if insert_cols:
        sql = f"""
            INSERT INTO trinity_medical_facility_doctors_external ({', '.join(insert_cols)})
            SELECT {', '.join(select_cols)}
            FROM trinity_doctor_external
            WHERE id NOT IN (SELECT id FROM trinity_medical_facility_doctors_external);
        """
        cr.execute(sql)

    # Update sequences if needed
    cr.execute("""
        SELECT setval('trinity_medical_facility_id_seq',
            (SELECT MAX(id) FROM trinity_medical_facility) + 1, false)
        WHERE EXISTS (SELECT 1 FROM trinity_medical_facility);
    """)

    cr.execute("""
        SELECT setval('trinity_medical_facility_doctors_id_seq',
            (SELECT MAX(id) FROM trinity_medical_facility_doctors) + 1, false)
        WHERE EXISTS (SELECT 1 FROM trinity_medical_facility_doctors);
    """)

    cr.execute("""
        SELECT setval('trinity_medical_facility_doctors_deductions_id_seq',
            (SELECT MAX(id) FROM trinity_medical_facility_doctors_deductions) + 1, false)
        WHERE EXISTS (SELECT 1 FROM trinity_medical_facility_doctors_deductions);
    """)

    cr.execute("""
        SELECT setval('trinity_medical_facility_doctors_external_id_seq',
            (SELECT MAX(id) FROM trinity_medical_facility_doctors_external) + 1, false)
        WHERE EXISTS (SELECT 1 FROM trinity_medical_facility_doctors_external);
    """)
