<?php

$config = array(

    'admin' => array(
        'core:AdminPassword',
    ),

    'example-userpass' => array(
        'exampleauth:UserPass',
        'admin:admin' => array(
            'uid' => array('1'),
            'email' => 'user2@example.com',
            'username' => 'admin',
            'first_name' => 'IT',
            'last_name' => 'Guy'
        ),
        'familieleder:sagsbehandler' => array(
            'uid' => array('2'),
            'email' => 'user2@example.com',
            'username' => 'familieleder',
            'first_name' => 'Familie',
            'last_name' => 'Leder'
        ),
        'familieraadgiver:sagsbehandler' => array(
            'uid' => array('3'),
            'email' => 'user2@example.com',
            'username' => 'familieraadgiver',
            'first_name' => 'Familie',
            'last_name' => 'Raadgiver'
        ),
        'ungeleder:sagsbehandler' => array(
            'uid' => array('4'),
            'email' => 'user2@example.com',
            'username' => 'ungeleder',
            'first_name' => 'Unge',
            'last_name' => 'Leder'
        ),
        'ungeraadgiver:sagsbehandler' => array(
            'uid' => array('5'),
            'email' => 'user2@example.com',
            'username' => 'ungeraadgiver',
            'first_name' => 'Unge',
            'last_name' => 'Raadgiver'
        ),
    ),

);

