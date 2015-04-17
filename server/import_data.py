# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import csv
import re
import sys
from datetime import datetime
import server.models as models


def pattern_or_none(reg_exp, string_input):
    r = re.search(reg_exp, string_input)
    if r:
        try:
            return r.group(0)
        except IndexError:
            pass  # not found
    return None


def dot():
    sys.stdout.write('.')
    sys.stdout.flush()


def import_owners():
    with open('server/owners.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=str(','), quotechar=str('|'))
        for row in reader:
            dot()
            
            address1 = row[6]
            city = ''
            for c in ['Brooklyn', 'New York', 'Queens', 'Woodside', 'Bronx', 'Jamaica']:
                if c in address1:
                    city = c
                    address1 = ''.join(address1.split(c))

            zipcode = pattern_or_none(r'\d{5}', address1) or ''
            if zipcode:
                address1 = ''.join(address1.split(zipcode))

            state_code = 'NY'
            address1 = ''.join(address1.split(' NY'))

            s = row[10].lower()
            if s == "yes":
                split = True
            elif s == 'no':
                split = False
            else:
                split = None

            try:
                rating = int(row[1])
            except Exception as e:
                if row[1].lower() == "out of range".lower():
                    rating = 3
                    state_code = ''
                else:
                    rating = None

            if row[7]:
                date = datetime.strptime(row[7], "%m/%d/%Y")
            else:
                date = None

            company_name = row[2]
            if company_name.lower() == 'individual':
                company_name = ''

            owner = models.Owner(
                pk = row[0],
                company_name = company_name,
                address1 = address1,
                city = city,
                state_code = 'NY',
                zipcode = zipcode,
                split_shift = split,
                rating = rating,
                last_engagement = date,
            )
            try:
                owner.save()

                # now load the user_account data for that owner
                try:
                    (first, last) = row[3].split(' ')
                except ValueError:
                    first = row[3]
                    last = ''

                user_account = models.UserAccount(
                    first_name = first,
                    last_name = last,
                    phone_number = row[4],
                    email = row[5] or None,
                    owner = owner,
                )
                try:
                    user_account.save()
                except Exception as e:
                    print e

            except Exception as e:
                print e


def setup_make_models():
    with open('server/vehicles.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=str(','), quotechar=str('|'))
        for row in reader:
            dot()
            mod = models.MakeModel(
                make = row[3].strip(),
                model = row[4].strip(),
            )
            if not models.MakeModel.objects.filter(make=mod.make, model=mod.model).exists():
                mod.save()


def import_cars():
    with open('server/vehicles.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=str(','), quotechar=str('|'))
        for row in reader:
            dot()

            notes = row[15]

            # get owner_id
            try:
                owner_id = int(row[11])
            except Exception as e:
                print e
                continue

            # get status
            status = pattern_or_none(r"[a-z,A-Z]+", row[1])
            if not status in ['Available', 'Unknown', 'Busy']:
                notes = status + notes
                status = 'Unknown'

            # get makemodel
            make = row[3].strip()
            model = row[4].strip()
            make_model = models.MakeModel.objects.get(make=make, model=model)

            if row[2]:
                next_available_date = datetime.strptime(row[2], "%m/%d/%Y")
            else:
                next_available_date = None

            year = None
            if row[5]:
                try:
                    year = int(row[5])
                except Exception:
                    pass

            solo_cost = pattern_or_none(r'[\d\.]+', row[7])
            split_cost = pattern_or_none(r'[\d\.]+', row[8])
            solo_deposit = pattern_or_none(r'[\d\.]+', row[9])

            minl = '_0_unknown'
            count = pattern_or_none(r'[\d]+', row[10] + notes)
            if count:
                if 'month' in notes.lower() or 'month' in row[10]:
                    try:
                        minl = [
                            '_5_one_month',
                            '_7_two_months',
                            '_08_three_months',
                            '_09_four_months',
                            '_10_five_months',
                            '_11_six_months',
                        ][int(count)]
                    except IndexError:
                        pass
                elif 'week' in notes.lower() or 'week' in row[10]:
                    try:
                        minl = {
                            1: '_2_one_week',
                            2: '_3_two_weeks',
                            3: '_4_three_weeks',
                            6: '_6_six_weeks',
                        }[count]
                    except KeyError:
                        pass

            car = models.Car(
                pk = int(row[0]),
                owner = models.Owner.objects.get(pk=owner_id),
                status = status.lower(),
                next_available_date = next_available_date,
                make_model = make_model,
                year = year,
                plate = row[6],
                solo_cost = solo_cost,
                solo_deposit = solo_deposit,
                split_cost = split_cost,
                min_lease = minl,
                notes = notes,
            )
            try:
                car.save()
            except Exception as e:
                print e

def delete_data():
    models.UserAccount.objects.all().delete()
    models.Owner.objects.all().delete()
    models.Car.objects.all().delete()
    models.MakeModel.objects.all().delete()

def run_import():
    import_owners()
    setup_make_models()
    import_cars()
