try:
            params =[]
            factors=[]
            hard_passes=[]
            easy_passes=[]
            generic_config_info=[]
            subjects=[]
            turmas=[]
            prereqs=[]
            semoffers=[]
            credits=[]
            cat_info=[]
            prereq_report=[]
            f=open('app/imports/uploads/catalogo.xml')
            subjects = getting_subjects_config_from_file('app/imports/uploads/catalogo.xml')
            turmas = getting_turmas_config_from_file('app/imports/uploads/catalogo.xml')
            prereqs = getting_prereqs_config_from_file('app/imports/uploads/catalogo.xml')
            semoffers = getting_semoffer_config_from_file('app/imports/uploads/catalogo.xml')
            credits = getting_credits_config_from_file('app/imports/uploads/catalogo.xml')
            cat_info = getting_catalog_info_from_file('app/imports/uploads/catalogo.xml')
            prereq_report = getting_prereq_report_from_file('app/imports/uploads/catalogo.xml')
            f=open('app/imports/uploads/configs.xml')
            params = getting_params_config_from_file('app/imports/uploads/configs.xml')
            factors = getting_factors_config_from_file('app/imports/uploads/configs.xml')
            hard_passes = getting_hard_pass_from_file('app/imports/uploads/configs.xml')
            easy_passes = getting_easy_pass_from_file('app/imports/uploads/configs.xml')
            generic_config_info = getting_generic_info_from_file('app/imports/uploads/configs.xml')
            simulation_lock = False
        except:
            simulation_lock = True
            pass
