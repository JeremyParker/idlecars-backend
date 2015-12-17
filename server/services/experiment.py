# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from experiments import experiments


def get_referral_rewards(driver):
    '''
    Returns a (invitee credit, invitor credit) tuple, to assign to the credit code that
    an existing driver will get. How much credit can they give to referrals? How much will
    they get as a reward?
    '''
    cohort_id = experiments.assign_alternative(driver.auth_user.username, 'referral_rewards')
    if 'default' == cohort_id:
        return ('75.00', '25.00')
    else:
        return ('50.00', '50.00')


def referral_reward_converted(invitor_customer):
    '''
    This function records when a driver invited someone, and that person converted.
    '''
    experiments.increment_conversion(invitor_customer.user.username, 'referral_rewards')


def get_inactive_credit(driver):
    '''
    Return a credit amount that we grant to inactive drivers.
    '''
    cohort_id = experiments.assign_alternative(driver.auth_user.username, 'inactive_credit')
    if 'default' == cohort_id:
        return '50.00'
    elif 'inactive_100' == cohort_id:
        return '100.00'
    else:
        return '150.00'
