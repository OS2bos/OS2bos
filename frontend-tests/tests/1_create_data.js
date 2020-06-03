// Testing with Testcafe : https://devexpress.github.io/testcafe/documentation/getting-started/

import { Selector, RequestLogger } from 'testcafe'
import { login } from '../utils/logins.js'
import { createActivity } from '../utils/crud.js'
import { axe } from '../utils/axe.js'
import baseurl from '../utils/url.js'

function leadZero(number) {
    if (number < 10) {
        return `0${ number }`
    } else {
        return number
    }
}

function makeDateStr(date, offset) {
    let new_date = new Date(date.setMonth(date.getMonth() + offset + 1))
    return `${new_date.getFullYear()}-${leadZero(new_date.getMonth() + 1)}-01`
}

let today = new Date(),
    rand = Math.floor(Math.random() * 100 )

let str1mth = makeDateStr(today, 1),
    str2mth = makeDateStr(today, 2),
    str5mth = makeDateStr(today, 5),
    str10mth = makeDateStr(today, 10),
    str15mth = makeDateStr(today, 15)
    
const testdata = {
    case1: {
        id: 1,
        name: `xx.xx.xx-${ rand }-yy`
    },
    appr1: {
        id: 1,
        name: `xx.xx.xx-${ rand }-bevil${ rand }`,
        section: 'SEL-109 Botilbud, kriseramte kvinder'
    },
    appr2: {
        id: 2,
        name: `xx.xx.xx-${ rand }-bevil${ rand }`,
        section: 'SEL-54-a Tilknytning af koordinator'
    },
    act1: {
        type: 1,
        start: str1mth,
        end: str10mth,
        note: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
        amount: '3095.50',
        payee_id: '78362883763',
        payee_name: 'Fiktivt Firma ApS'
    },
    act2: {
        type: 1,
        start: str2mth,
        end: str5mth,
        note: 'En lille note',
        amount: '595.95',
        payee_id: '8923',
        payee_name: 'Testbevillingscentralen A/S'
    },
    act3: {
        type: 1,
        start: str5mth,
        end: str10mth,
        note: 'En anden lille note',
        amount: '150',
        payee_id: '8937-2342-2342',
        payee_name: 'TESTiT A/S'
    },
    act4: {
        expected_type: 'adjustment',
        type: 1,
        start: str2mth,
        end: str15mth,
        note: 'Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
        amount: '3595.50',
        payee_id: '78362883763',
        payee_name: 'Fiktivt Firma ApS'
    },
    act5: {
        expected_type: 'expectation',
        type: 1,
        start: str2mth,
        end: str5mth,
        note: 'En anden lille note',
        amount: '9.95',
        payee_id: '8937-2342-2342',
        payee_name: 'TESTiT A/S'
    },
    act6: {
        type: 1,
        start: str2mth,
        end: str5mth,
        note: 'Denne ydelse vil blive slettet',
        amount: '999.95',
        payee_id: '8937-2342-2342',
        payee_name: 'TESTiT A/S'
    },
    act7: {
        type: 2,
        start: str2mth,
        note: 'Bemærk denne lille note',
        amount: '750',
        payee_id: '3337-4123-1221',
        payee_name: 'TEST-DATA A/S'
    }
}

fixture('Create some data') // declare the fixture
    .page(baseurl)  // specify the start page
    .beforeEach(async t => { 
        await login(t) 
    })

test('Create Case', async t => {
    
    await t.click(Selector('button').withText('+ Tilknyt hovedsag'))
    
    await axe(t)

    await t
        .typeText('#field-sbsys-id', testdata.case1.name)
        .typeText('#field-cpr', '000000-0000')
        .click('#selectTargetGroup')
        .click(Selector('#selectTargetGroup option').withText('Familieafdelingen'))
        .click('#selectDistrict')
        .click(Selector('#selectDistrict option').withText('Baltorp'))
        .click('#field-indsatstrappe')
        .click(Selector('#field-indsatstrappe option').withText('Trin 3: Hjemmebaserede indsatser'))
        .click('#field-skaleringstrappe')
        .click(Selector('#field-skaleringstrappe option').withText('5'))
        .click(Selector('input').withAttribute('type', 'submit'))
        .click(Selector('a.header-link'))
        .expect(Selector('.cases table a').withText(testdata.case1.name)).ok()
    
    await axe(t)
})

test('Create Appropriation', async t => {

    await t
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('.appropriation-create-btn'))
    
    await axe(t)

    await t
        .typeText('#field-sbsysid', testdata.appr1.name)
        .click('#field-lawref')
        .click(Selector('#field-lawref option').withText(testdata.appr1.section))
        .click(Selector('input').withAttribute('type', 'submit'))
        .click(Selector('a.header-link'))
        .click(Selector('a').withText(testdata.case1.name))
        .expect(Selector('.datagrid-action a').innerText).contains(testdata.appr1.name)
    
    await axe(t)
})

test('Create activities', async t => {

    await t
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr1.name))
    
    await createActivity(t, testdata.act1)
    await createActivity(t, testdata.act2)
    await createActivity(t, testdata.act3)

    await t
        .click(Selector('a.header-link'))
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr1.name))

    testdata.act1.act_detail = await Selector('.activities table tr.act-list-item a').nth(0).innerText

    await t.expect(Selector('.activities table tr.act-list-item a').exists).ok()
    
    await axe(t)
})

test('Approve appropriation', async t => {

    await t
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr1.name))
        .click('#check-all')
        .click(Selector('button').withText('Godkend valgte'))
    
    await axe(t)

    await t
        .click(Selector('label').withAttribute('for','radio-btn-1'))
        .typeText('#field-text', 'Godkendt grundet svære og særligt tvingende omstændigheder')
        .click('button[type="submit"]')
        .expect(Selector('.mini-label .label-GRANTED').exists).ok()
    
    await axe(t)
})

test('Add adjustment activities', async t => {
    
    await t
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr1.name))
        .click(Selector('a').withText(testdata.act1.act_detail))
    
    await createActivity(t, testdata.act4)

    await t
        .click(Selector('a.header-link'))
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr1.name))
    
    await createActivity(t, testdata.act5)
    
    await t
        .expect(Selector('.label-EXPECTED')).ok()
        .expect(Selector('h1').withText('Bevillingsskrivelse').exists).ok()
    
    await axe(t)
})

test('Create appropriation with one main activity option', async t => {

    await t
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('.appropriation-create-btn'))
    
    await axe(t)

    await t
        .typeText('#field-sbsysid', testdata.appr2.name)
        .click('#field-lawref')
        .click(Selector('#field-lawref option').withText(testdata.appr2.section))
        .click(Selector('input').withAttribute('type', 'submit'))
        .click(Selector('a.header-link'))
        .click(Selector('a').withText(testdata.case1.name))
        .expect(Selector('.datagrid-action a').innerText).contains(testdata.appr2.name)
    
    await axe(t)
})

test('Create activities with one main activity option', async t => {

    await t
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr2.name))
    
    await createActivity(t, testdata.act7)

    await t
        .click(Selector('a.header-link'))
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr2.name))

    testdata.act1.act_detail = await Selector('.activities table tr.act-list-item a').nth(0).innerText

    await t.expect(Selector('.activities table tr.act-list-item a').exists).ok()
    
    await axe(t)
})

test('Approve appropriation with one main activity option', async t => {

    await t
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr2.name))
        .click('#check-all')
        .click(Selector('button').withText('Godkend valgte'))
    
    await axe(t)

    await t
        .click(Selector('label').withAttribute('for','radio-btn-3'))
        .typeText('#field-text', 'Godkendt grundet svære omstændigheder')
        .click('button[type="submit"]')
        .expect(Selector('.mini-label .label-GRANTED').exists).ok()
    
    await axe(t)
})
